"""Phase 1: build ml/data/processed/{train,val,test}/<class>/ from RoCoLe, DECAFIA and BRACOL.

Image-level labels, duplicate removal, group-aware 70/15/15 split stratified by
(source, class) and outputs/dataset_stats.json. Every rule applied here is recorded
in docs/decisiones.md; the v2 changes follow docs/PLAN_reentrenamiento_v2.md (R1, R2).
"""
import csv
import hashlib
import json
import random
import re
import shutil
from collections import Counter, defaultdict
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw

from config import (CLASSES, DATA_DIR, OUTPUTS_DIR, PROCESSED_DIR, PROCESSED_MAX_SIDE, RAW_DIR, SEED, SPLITS,
                    processed_name)

ROCOLE_DIR = RAW_DIR / "rocole"
DECAFIA_DIR = RAW_DIR / "decafia" / "CoffeeLeaf-CO"
BRACOL_DIR = DATA_DIR / "external" / "bracol" / "x" / "coffee-datasets" / "coffee-datasets" / "leaf"
REVIEW_DIR = DATA_DIR / "review"  # contact sheets for the manual check; never versioned

SPLIT_FRACTIONS = {"train": 0.70, "val": 0.15, "test": 0.15}
# Acceptance check of the split (plan v2, R1): strata this big must be this close to the target.
BALANCE_MIN_STRATUM = 40
BALANCE_TOLERANCE = 0.05
# Leaf boxes of the manifest: narrower or shorter than this fraction of the image is not a usable box.
MIN_LEAF_BOX_SIDE = 0.05
PROCESSED_JPEG_QUALITY = 92
ROCOLE_CLASS_MAP = {
    "healthy": "sana",
    "rust_level_1": "roya",
    "rust_level_2": "roya",
    "rust_level_3": "roya",
    "rust_level_4": "roya",
    "red_spider_mite": "arana_roja",
}
DECAFIA_NAMES = {0: "roya", 1: "coco", 2: "hojas", 3: "minador"}
# SANAS_ROCOLE_* are declared by DECAFIA as re-annotated RoCoLe images; the
# originals are already loaded from RoCoLe with their plant grouping.
DECAFIA_DERIVED_PREFIXES = ("SANAS_ROCOLE",)
# BRACOL `predominant_stress`; the other values (3, 4, 5) are not classes of this model.
BRACOL_CLASS_MAP = {0: "sana", 1: "minador", 2: "roya"}

# 256-bit dHash, compared over the 8 rotations/mirrors of each image. Thresholds
# were chosen by looking at sampled pairs per distance (docs/decisiones.md).
HASH_SIDE = 16
DUPLICATE_MAX_DISTANCE = 40  # same picture: keep one copy
RELATED_MAX_DISTANCE = 52  # possible copies or look-alikes: kept, forced into the same split
# BRACOL is one flat leaf per picture, always centred on a plain light background, so
# the hash only sees the silhouette: the closest BRACOL pairs (distance 19 to 35) and the
# closest BRACOL-DECAFIA pairs (40 to 43) were looked at and are all different leaves.
# Pairs that involve these sources are compared by MD5 only.
MD5_ONLY_SOURCES = ("bracol",)
POPCOUNT = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def load_rocole():
    items, discarded = [], Counter()
    for entry in json.loads((ROCOLE_DIR / "RoCoLE-json.json").read_text()):
        name = entry["External ID"]
        label = ROCOLE_CLASS_MAP.get(entry["Label"]["classification"])
        if label is None:
            discarded[f"rocole_not_v1:{entry['Label']['classification']}"] += 1
            continue
        plant = re.match(r"C\d+P\d+", name).group(0)
        items.append({
            "source": "rocole",
            "name": name.rsplit(".", 1)[0],
            "path": ROCOLE_DIR / "export" / f"{entry['ID']}.jpeg",
            "label": label,
            "group": f"rocole:{plant}",
            # Leaf outlines, in pixels of the original image.
            "leaf_points": [(point["x"], point["y"]) for leaf in entry["Label"].get("Leaf", [])
                            for point in leaf["geometry"]],
        })
    return items, discarded


def decafia_label(label_file):
    """Dominant-class rule: most instances among disease classes; ties are discarded."""
    counts = Counter(DECAFIA_NAMES[int(line.split()[0])]
                     for line in label_file.read_text().splitlines() if line.strip())
    counts.pop("hojas", None)
    if not counts:
        return "sana", None
    ranked = counts.most_common()
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return None, "decafia_tie"
    if ranked[0][0] not in CLASSES:
        return None, f"decafia_not_v1:{ranked[0][0]}"
    return ranked[0][0], None


def load_decafia():
    items, discarded = [], Counter()
    for image in sorted((DECAFIA_DIR / "images").glob("*/*.jpg")):
        prefix = re.match(r"[A-Za-z_]+", image.stem).group(0).rstrip("_")
        if prefix in DECAFIA_DERIVED_PREFIXES:
            discarded["decafia_derived_from_rocole"] += 1
            continue
        label_file = DECAFIA_DIR / "labels" / image.parent.name / f"{image.stem}.txt"
        label, reason = decafia_label(label_file)
        if label is None:
            discarded[reason] += 1
            continue
        items.append({
            "source": "decafia",
            "name": image.stem,
            "path": image,
            "label": label,
            "group": f"decafia:{image.stem}",
            "label_file": label_file,
        })
    return items, discarded


def is_readable(path):
    """True when the whole image decodes (the published BRACOL archive is truncated)."""
    try:
        with Image.open(path) as image:
            image.load()
        return True
    except (OSError, SyntaxError, ValueError):
        return False


def load_bracol():
    items, discarded = [], Counter()
    with open(BRACOL_DIR / "dataset.csv", newline="") as handle:
        rows = list(csv.DictReader(handle))
    candidates = []
    for row in rows:
        stress = int(row["predominant_stress"])
        label = BRACOL_CLASS_MAP.get(stress)
        path = BRACOL_DIR / "images" / f"{row['id']}.jpg"
        if label is None:
            discarded[f"bracol_not_v1:predominant_stress_{stress}"] += 1
        elif not path.is_file():
            discarded["bracol_image_missing"] += 1
        else:
            candidates.append((row["id"], label, path))
    with Pool() as pool:
        readable = pool.map(is_readable, [path for _, _, path in candidates], chunksize=16)
    for (name, label, path), ok in zip(candidates, readable):
        if not ok:
            discarded["bracol_image_unreadable"] += 1
            continue
        items.append({
            "source": "bracol",
            "name": name,
            "path": path,
            "label": label,
            "group": f"bracol:{name}",  # one leaf per image; look-alikes are merged later
        })
    return items, discarded


def fingerprint(path):
    """MD5 of the file plus the dHash of its 8 orientations."""
    md5 = hashlib.md5(path.read_bytes()).hexdigest()
    image = Image.open(path)
    image.draft("L", (256, 256))
    image = image.convert("L")
    hashes = []
    for mirrored in (False, True):
        base = image.transpose(Image.FLIP_LEFT_RIGHT) if mirrored else image
        for angle in (0, 90, 180, 270):
            small = np.asarray(base.rotate(angle, expand=True).resize((HASH_SIDE + 1, HASH_SIDE), Image.BILINEAR),
                               dtype=np.int16)
            hashes.append(np.packbits((small[:, 1:] > small[:, :-1]).flatten()))
    return md5, np.stack(hashes)


def min_distances(index, variants):
    """Distance from image `index` to every later image, minimised over orientations.

    Rotating and resizing is not exactly reversible, so both directions are compared
    to keep the distance symmetric.
    """
    rest = variants[index + 1:]
    forward = POPCOUNT[np.bitwise_xor(variants[index, 0][None, None, :], rest)].sum(axis=-1).min(axis=1)
    backward = POPCOUNT[np.bitwise_xor(variants[index][None, :, :], rest[:, :1, :])].sum(axis=-1).min(axis=1)
    return np.minimum(forward, backward)


def close_to_later(index, items, variants, max_distance):
    """Mask over the images after `index`: perceptually within `max_distance` of it."""
    close = min_distances(index, variants) <= max_distance
    md5_only = np.array([item["source"] in MD5_ONLY_SOURCES for item in items[index:]])
    return close & ~md5_only[1:] & ~md5_only[0]


class UnionFind:
    def __init__(self, keys):
        self.parent = {k: k for k in keys}

    def find(self, key):
        while self.parent[key] != key:
            self.parent[key] = self.parent[self.parent[key]]
            key = self.parent[key]
        return key

    def union(self, a, b):
        self.parent[self.find(a)] = self.find(b)


def remove_duplicates(items, variants):
    """Keep one image per duplicate cluster; drop clusters with conflicting labels."""
    clusters = UnionFind(range(len(items)))
    for i in range(len(items) - 1):
        for j in np.nonzero(close_to_later(i, items, variants, DUPLICATE_MAX_DISTANCE))[0]:
            clusters.union(i, i + 1 + int(j))
    for i, j in pairs_with_same_md5(items):
        clusters.union(i, j)

    members = defaultdict(list)
    for i in range(len(items)):
        members[clusters.find(i)].append(i)

    kept, stats = [], Counter()
    for indexes in members.values():
        if len(indexes) == 1:
            kept.append(indexes[0])
            continue
        if len({items[i]["label"] for i in indexes}) > 1:
            stats["duplicates_conflicting_labels"] += len(indexes)
            continue
        # RoCoLe copies win: they carry the plant identifier used for grouping.
        winner = min(indexes, key=lambda i: (items[i]["source"] != "rocole", items[i]["name"]))
        kept.append(winner)
        stats["duplicates_removed"] += len(indexes) - 1
        if len({items[i]["source"] for i in indexes}) > 1:
            stats["duplicates_across_datasets"] += len(indexes) - 1
    kept.sort()
    return kept, stats


def pairs_with_same_md5(items):
    by_md5 = defaultdict(list)
    for i, item in enumerate(items):
        by_md5[item["md5"]].append(i)
    return [(idx[0], other) for idx in by_md5.values() for other in idx[1:]]


def merge_related_groups(items, variants):
    """Look-alike images must share a split, so their groups are merged."""
    groups = UnionFind({item["group"] for item in items})
    for i in range(len(items) - 1):
        for j in np.nonzero(close_to_later(i, items, variants, RELATED_MAX_DISTANCE))[0]:
            groups.union(items[i]["group"], items[i + 1 + int(j)]["group"])
    for item in items:
        item["group"] = groups.find(item["group"])


def stratum(item):
    return item["source"], item["label"]


def split_by_group(items, fractions=SPLIT_FRACTIONS, seed=SEED, key="split"):
    """Greedy group-aware split stratified by (source, class).

    Writes into `item[key]` one of the names of `fractions` (name -> target fraction);
    cv_experimentos.py reuses it to build folds.

    Each group goes whole to the split that stays emptiest relative to its target
    (assigned / target) in the strata the group holds. v1 compared absolute class
    counts, which sent the big groups (RoCoLe plants) to train and left that source
    almost out of val and test (docs/bitacora.md, R0).
    """
    groups = defaultdict(list)
    for item in items:
        groups[item["group"]].append(item)
    totals = Counter(stratum(item) for item in items)
    assigned = {split: Counter() for split in fractions}

    order = sorted(groups)
    random.Random(seed).shuffle(order)
    # Stable: big groups first (the hardest to fit), seeded order within a size. The
    # single-image groups that follow even out whatever the big ones left unbalanced.
    order.sort(key=lambda g: -len(groups[g]))
    for group in order:
        strata = Counter(stratum(item) for item in groups[group])

        def fill_after(split):
            return sum(n * (assigned[split][stratum_key] + n) / (fractions[split] * totals[stratum_key])
                       for stratum_key, n in strata.items())

        best = min(fractions, key=fill_after)  # ties resolve in the order of `fractions`
        assigned[best].update(strata)
        for item in groups[group]:
            item[key] = best


def stratum_split_fractions(items):
    totals = Counter(stratum(item) for item in items)
    assigned = Counter((*stratum(item), item["split"]) for item in items)
    return {f"{source}/{label}": {split: round(assigned[(source, label, split)] / total, 4) for split in SPLITS}
            for (source, label), total in sorted(totals.items())}


def check_source_balance(items):
    """Acceptance check (plan v2, R1): every source is represented alike in the three splits."""
    totals = Counter(stratum(item) for item in items)
    fractions = stratum_split_fractions(items)
    failures, worst, checked = [], 0.0, 0
    for (source, label), total in sorted(totals.items()):
        if total < BALANCE_MIN_STRATUM:
            continue
        checked += 1
        for split in SPLITS:
            deviation = abs(fractions[f"{source}/{label}"][split] - SPLIT_FRACTIONS[split])
            worst = max(worst, deviation)
            if deviation > BALANCE_TOLERANCE:
                failures.append(f"{source}/{label} {split}: {fractions[f'{source}/{label}'][split]}")
    return {"passed": not failures,
            "min_stratum_images": BALANCE_MIN_STRATUM,
            "tolerance": BALANCE_TOLERANCE,
            "strata_checked": checked,
            "strata_too_small": {f"{source}/{label}": total for (source, label), total in sorted(totals.items())
                                 if total < BALANCE_MIN_STRATUM},
            "worst_deviation": round(worst, 4),
            "failures": failures}


def write_downscaled(job):
    """RGB JPEG with the longest side at most PROCESSED_MAX_SIDE; never upscaled.

    EXIF orientation is deliberately not applied: v1 copied the files and TensorFlow
    decodes them without reading EXIF, so the stored pixels keep that orientation.
    """
    source, target = job
    with Image.open(source) as image:
        image = image.convert("RGB")
        if max(image.size) > PROCESSED_MAX_SIDE:
            scale = PROCESSED_MAX_SIDE / max(image.size)
            size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
            image = image.resize(size, Image.LANCZOS)
        image.save(target, "JPEG", quality=PROCESSED_JPEG_QUALITY)


def write_processed(items):
    for split in SPLITS:
        shutil.rmtree(PROCESSED_DIR / split, ignore_errors=True)
    for item in items:
        target = PROCESSED_DIR / item["split"] / item["label"]
        target.mkdir(parents=True, exist_ok=True)
        item["output"] = target / processed_name(item["source"], item["name"])
    with Pool() as pool:
        pool.map(write_downscaled, [(item["path"], item["output"]) for item in items], chunksize=16)


def leaf_box(item):
    """[x0, y0, x1, y1] of the leaf, normalized to 0..1 in the image, or None.

    The processed image is the original one downscaled, so the normalized box holds for both.
    """
    if item["source"] == "rocole":
        if not item["leaf_points"]:
            return None
        with Image.open(item["path"]) as image:
            width, height = image.size
        xs, ys = zip(*item["leaf_points"])
        box = [min(xs) / width, min(ys) / height, max(xs) / width, max(ys) / height]
    elif item["source"] == "decafia":
        rows = [[float(value) for value in line.split()[1:5]]
                for line in item["label_file"].read_text().splitlines()
                if line.strip() and DECAFIA_NAMES[int(line.split()[0])] == "hojas"]
        if not rows:
            return None
        box = [min(cx - w / 2 for cx, _, w, _ in rows), min(cy - h / 2 for _, cy, _, h in rows),
               max(cx + w / 2 for cx, _, w, _ in rows), max(cy + h / 2 for _, cy, _, h in rows)]
    else:
        return None
    x0, y0, x1, y1 = (min(1.0, max(0.0, value)) for value in box)
    if x1 - x0 < MIN_LEAF_BOX_SIDE or y1 - y0 < MIN_LEAF_BOX_SIDE:
        return None
    return [round(value, 4) for value in (x0, y0, x1, y1)]


def write_manifest(items):
    """One entry per processed image; read by cv_experimentos.py. Returns the entries."""
    manifest = [{"file": item["output"].relative_to(PROCESSED_DIR).as_posix(),
                 "source": item["source"],
                 "label": item["label"],
                 "split": item["split"],
                 "group": item["group"],
                 "leaf_box": leaf_box(item)} for item in items]
    (PROCESSED_DIR / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return manifest


def verify_no_leakage(items, variants):
    """Acceptance check, recomputed from the final assignment."""
    by_md5 = defaultdict(set)
    for item in items:
        by_md5[item["md5"]].add(item["split"])
    md5_leaks = sum(1 for splits in by_md5.values() if len(splits) > 1)

    splits = np.array([item["split"] for item in items])
    perceptual_leaks = 0
    for i in range(len(items) - 1):
        close = close_to_later(i, items, variants, RELATED_MAX_DISTANCE)
        perceptual_leaks += int((close & (splits[i + 1:] != splits[i])).sum())
    groups = defaultdict(set)
    for item in items:
        groups[item["group"]].add(item["split"])
    group_leaks = sum(1 for s in groups.values() if len(s) > 1)
    return {"md5_in_two_splits": md5_leaks,
            "perceptual_pairs_in_two_splits": perceptual_leaks,
            "groups_in_two_splits": group_leaks}


def write_review_sheets(items, per_class=20, tile=224):
    """Contact sheet per class for the manual label check (plan phase 1, step 4)."""
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    for label in CLASSES:
        sample = rng.sample([i for i in items if i["label"] == label], per_class)
        columns = 5
        sheet = Image.new("RGB", (columns * tile, (per_class // columns) * (tile + 14)), "white")
        draw = ImageDraw.Draw(sheet)
        for n, item in enumerate(sample):
            image = Image.open(item["path"]).convert("RGB")
            image.thumbnail((tile, tile))
            x, y = (n % columns) * tile, (n // columns) * (tile + 14)
            sheet.paste(image, (x, y))
            draw.text((x + 2, y + tile), f"{item['source']}:{item['name']}"[:36], fill="black")
        sheet.save(REVIEW_DIR / f"{label}.jpg", quality=85)


def main():
    rocole, discarded = load_rocole()
    decafia, decafia_discarded = load_decafia()
    bracol, bracol_discarded = load_bracol()
    discarded.update(decafia_discarded)
    discarded.update(bracol_discarded)
    items = rocole + decafia + bracol
    loaded = Counter(item["source"] for item in items)

    with Pool() as pool:
        prints = pool.map(fingerprint, [item["path"] for item in items], chunksize=32)
    for item, (md5, _) in zip(items, prints):
        item["md5"] = md5
    variants = np.stack([hashes for _, hashes in prints])

    kept, duplicate_stats = remove_duplicates(items, variants)
    items, variants = [items[i] for i in kept], variants[kept]
    merge_related_groups(items, variants)
    split_by_group(items)
    write_processed(items)
    manifest = write_manifest(items)
    write_review_sheets(items)

    counts = {split: {label: 0 for label in CLASSES} for split in SPLITS}
    by_source = {label: Counter() for label in CLASSES}
    sources = sorted({item["source"] for item in items})
    counts_by_source = {split: {source: {label: 0 for label in CLASSES} for source in sources} for split in SPLITS}
    for item in items:
        counts[item["split"]][item["label"]] += 1
        by_source[item["label"]][item["source"]] += 1
        counts_by_source[item["split"]][item["source"]][item["label"]] += 1
    balance = check_source_balance(items)
    per_class = {label: sum(counts[s][label] for s in SPLITS) for label in CLASSES}
    group_sizes = Counter(item["group"] for item in items)

    stats = {
        "seed": SEED,
        "classes": CLASSES,
        "split_fractions_target": SPLIT_FRACTIONS,
        "raw_images": {"rocole": len(list((ROCOLE_DIR / "export").glob("*.jpeg"))),
                       "decafia": len(list((DECAFIA_DIR / "images").glob("*/*.jpg"))),
                       "bracol": len(list((BRACOL_DIR / "images").glob("*.jpg")))},
        "loaded_after_label_rules": dict(loaded),
        "discarded_by_rule": dict(sorted(discarded.items())),
        "duplicates": {"duplicate_max_distance": DUPLICATE_MAX_DISTANCE,
                       "related_max_distance": RELATED_MAX_DISTANCE,
                       "md5_only_sources": list(MD5_ONLY_SOURCES),
                       **{k: int(v) for k, v in sorted(duplicate_stats.items())}},
        "final_images": len(items),
        "processed_max_side": PROCESSED_MAX_SIDE,
        "counts": counts,
        "counts_by_source": counts_by_source,
        "per_class_total": per_class,
        "per_class_by_source": {label: dict(c) for label, c in by_source.items()},
        "split_fractions_actual": {
            label: {s: round(counts[s][label] / per_class[label], 4) for s in SPLITS} for label in CLASSES},
        "stratum_split_fractions": stratum_split_fractions(items),
        "source_balance_check": balance,
        "imbalance_ratio_train": round(max(counts["train"].values()) / min(counts["train"].values()), 3),
        "groups": {"count": len(group_sizes), "largest": max(group_sizes.values())},
        "leakage_check": verify_no_leakage(items, variants),
        "manifest_images": len(manifest),
        "leaf_boxes": {source: sum(1 for entry in manifest
                                   if entry["source"] == source and entry["leaf_box"] is not None)
                       for source in sources},
    }
    OUTPUTS_DIR.mkdir(exist_ok=True)
    (OUTPUTS_DIR / "dataset_stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    if not balance["passed"]:
        raise SystemExit("Source balance check FAILED (target 70/15/15, tolerance "
                         f"{BALANCE_TOLERANCE}): {'; '.join(balance['failures'])}")


if __name__ == "__main__":
    main()
