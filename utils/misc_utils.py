def pop_multi(d: dict, keys: list[str]) -> dict:
    popped = {}
    for k in keys:
        if k in d:
            popped[k] = d.pop(k)
    return popped
