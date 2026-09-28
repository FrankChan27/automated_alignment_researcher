"""Minimal experiment: is Python list.sort() stable?"""

def main():
    # Pairs of (key, original_index) with duplicate keys
    items = [
        (2, 0),
        (1, 1),
        (2, 2),
        (1, 3),
        (3, 4),
        (1, 5),
        (2, 6),
    ]
    before = list(items)
    items.sort(key=lambda x: x[0])

    # For each distinct key, check that original_index order is preserved
    from collections import defaultdict
    by_key_before = defaultdict(list)
    for key, idx in before:
        by_key_before[key].append(idx)

    by_key_after = defaultdict(list)
    for key, idx in items:
        by_key_after[key].append(idx)

    stable = True
    for key in by_key_before:
        if by_key_before[key] != by_key_after[key]:
            stable = False
            print(f"UNSTABLE for key={key}: before={by_key_before[key]} after={by_key_after[key]}")

    print(f"input:  {before}")
    print(f"sorted: {items}")
    print(f"stable: {stable}")
    return 0 if stable else 1

if __name__ == "__main__":
    raise SystemExit(main())
