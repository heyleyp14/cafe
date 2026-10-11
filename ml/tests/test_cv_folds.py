"""Tests for the cross-validation folds of cv_experimentos.py, on synthetic items.

Run with `python tests/test_cv_folds.py` from ml/.
"""
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cv_experimentos as cv  # noqa: E402

FOLDS = 3
TOLERANCE = 0.08
MIN_STRATUM = 30
VALIDATION_TOLERANCE = 0.08


def synthetic_items():
    """Multi-image mixed-class groups (like RoCoLe plants) and single-image groups."""
    rng = random.Random(11)
    items = []

    def add(source, label, group):
        items.append({"file": f"{source}_{len(items)}.jpg", "source": source, "label": label, "group": group})

    for plant in range(120):
        for _ in range(rng.randint(2, 10)):
            add("plants", rng.choice(["roya", "sana", "sana", "arana_roja"]), f"plants:{plant}")
    for n in range(40):  # one large group
        add("plants", "roya" if n % 2 else "sana", "plants:large")
    for label, count in (("minador", 300), ("roya", 240), ("sana", 100)):
        for n in range(count):
            add("singles", label, f"singles:{label}{n}")
    for n in range(8):  # stratum below the minimum: not checked, must not break anything
        add("tiny", "sana", f"tiny:{n}")
    for n in range(10):  # look-alike merging joins sources and classes into one group
        add("singles", "minador", f"merged:{n}")
        add("plants", "roya", f"merged:{n}")
    return items


def run_folds(seed=42, folds=FOLDS):
    items = synthetic_items()
    cv.assign_folds(items, folds, seed)
    return items


def test_groups_never_span_folds():
    folds_by_group = defaultdict(set)
    for item in run_folds():
        folds_by_group[item["group"]].add(item["fold"])
    broken = {group: folds for group, folds in folds_by_group.items() if len(folds) > 1}
    assert not broken, broken


def test_every_item_is_tested_exactly_once():
    items = run_folds()
    tested = Counter()
    for fold in range(FOLDS):
        train, validation, test = cv.fold_partition(items, fold, seed=42)
        names = [{item["file"] for item in part} for part in (train, validation, test)]
        assert not (names[0] & names[1] or names[0] & names[2] or names[1] & names[2])
        assert len(train) + len(validation) + len(test) == len(items)
        assert all(item["fold"] == fold for item in test)
        tested.update(names[2])
    assert set(tested) == {item["file"] for item in items}
    assert set(tested.values()) == {1}


def test_validation_is_group_aware_and_about_15_percent():
    items = run_folds()
    for fold in range(FOLDS):
        train, validation, test = cv.fold_partition(items, fold, seed=42)
        groups = [{item["group"] for item in part} for part in (train, validation, test)]
        assert not (groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2])
        fraction = len(validation) / (len(train) + len(validation))
        assert abs(fraction - cv.VALIDATION_FRACTION) <= VALIDATION_TOLERANCE, fraction


def test_every_stratum_is_spread_over_the_folds():
    for folds in (2, 3, 5):
        items = run_folds(folds=folds)
        totals = Counter((item["source"], item["label"]) for item in items)
        assigned = Counter((item["source"], item["label"], item["fold"]) for item in items)
        checked, failures = 0, []
        for (source, label), total in sorted(totals.items()):
            if total < MIN_STRATUM:
                continue
            checked += 1
            for fold in range(folds):
                fraction = assigned[(source, label, fold)] / total
                if abs(fraction - 1 / folds) > TOLERANCE:
                    failures.append(f"K={folds} {source}/{label} fold {fold}: {fraction:.3f}")
        assert checked == 6, checked
        assert not failures, failures


def test_folds_are_deterministic():
    first = {item["file"]: item["fold"] for item in run_folds()}
    assert first == {item["file"]: item["fold"] for item in run_folds()}

    # The result must not depend on the order in which the items arrive.
    shuffled = synthetic_items()
    random.Random(3).shuffle(shuffled)
    cv.assign_folds(shuffled, FOLDS, 42)
    assert first == {item["file"]: item["fold"] for item in shuffled}

    assert first != {item["file"]: item["fold"] for item in run_folds(seed=7)}


def test_limit_keeps_whole_groups():
    items = synthetic_items()
    limited = cv.limit_groups(items, 5, seed=42)
    kept = {item["group"] for item in limited}
    assert len(limited) == sum(1 for item in items if item["group"] in kept)
    per_stratum = defaultdict(set)
    for item in limited:
        per_stratum[(item["source"], item["label"])].add(item["group"])
    assert all(len(groups) >= 5 for groups in per_stratum.values()), per_stratum


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
