items = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
result = sorted(items, key=lambda t: t[0])
expected_if_stable = [(1, "b"), (1, "d"), (2, "a"), (2, "c")]
stable = result == expected_if_stable
print("RESULT", result)
print("STABLE", stable)
