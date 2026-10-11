"""Tests for the group-aware split of 01_preparar_datos.py, on synthetic items.

Run with `python -m pytest tests/test_split.py` or `python tests/test_split.py` from ml/.
"""
import copy
import importlib
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
prepare = importlib.import_module("01_preparar_datos")  # the module name starts with a digit

TARGET = {"train": 0.70, "val": 0.15, "test": 0.15}
TOLERANCE = 0.05
MIN_STRATUM = 40


def synthetic_items():
    """Three sources: multi-image mixed-class groups (one of them large) and single images."""
    rng = random.Random(7)
    items = []

    def add(source, label, group):
        items.append({"source": source, "label": label, "group": group,
                      "name": f"{source}_{len(items)}"})

    # "plants": like RoCoLe, every group holds several leaves and may mix roya and sana.
    for plant in range(150):
        for _ in range(rng.randint(3, 12)):
            add("plants", rng.choice(["roya", "sana", "sana"]), f"plants:{plant}")
    for n in range(70):  # one large group
        add("plants", "roya" if n % 2 else "sana", "plants:large")

    # "singles" and "small": one image per group, three classes.
    for label, count in (("minador", 300), ("roya", 400), ("sana", 200)):
        for n in range(count):
            add("singles", label, f"singles:{label}{n}")
    for label, count in (("minador", 60), ("roya", 50), ("sana", 45)):
        for n in range(count):
            add("small", label, f"small:{label}{n}")
    for n in range(10):  # stratum below the minimum: not checked, must not break anything
        add("tiny", "sana", f"tiny:{n}")

    # Look-alike merging can join images of different sources and classes into one group.
    for n in range(12):
        add("singles", "minador", f"merged:{n}")
        add("small", "roya", f"merged:{n}")
        add("small", "minador", f"merged:{n}")
    return items


def run_split():
    items = synthetic_items()
    prepare.split_by_group(items)
    return items


def test_groups_are_never_split():
    splits_by_group = defaultdict(set)
    for item in run_split():
        assert item["split"] in TARGET
        splits_by_group[item["group"]].add(item["split"])
    broken = {group: splits for group, splits in splits_by_group.items() if len(splits) > 1}
    assert not broken, broken


def test_every_stratum_is_close_to_the_target():
    items = run_split()
    totals = Counter((item["source"], item["label"]) for item in items)
    assigned = Counter((item["source"], item["label"], item["split"]) for item in items)
    checked, failures = 0, []
    for (source, label), total in sorted(totals.items()):
        if total < MIN_STRATUM:
            continue
        checked += 1
        for split, target in TARGET.items():
            fraction = assigned[(source, label, split)] / total
            if abs(fraction - target) > TOLERANCE:
                failures.append(f"{source}/{label} {split}: {fraction:.3f} (target {target})")
    assert checked == 8, checked
    assert not failures, failures


def test_split_is_deterministic():
    first = [(item["name"], item["split"]) for item in run_split()]
    second = [(item["name"], item["split"]) for item in run_split()]
    assert first == second

    # The result must not depend on the order in which the items arrive.
    shuffled = synthetic_items()
    random.Random(3).shuffle(shuffled)
    prepare.split_by_group(shuffled)
    assert dict(first) == {item["name"]: item["split"] for item in shuffled}


def test_input_items_keep_their_fields():
    before = synthetic_items()
    after = copy.deepcopy(before)
    prepare.split_by_group(after)
    for old, new in zip(before, after):
        assert {k: v for k, v in new.items() if k != "split"} == old


if __name__ == "__main__":
    failed = 0
    for name, test in sorted(globals().items()):
        if name.startswith("test_") and callable(test):
            try:
                test()
                print(f"PASS {name}")
            except AssertionError as error:
                failed += 1
                print(f"FAIL {name}: {str(error)[:600]}")
    sys.exit(1 if failed else 0)
