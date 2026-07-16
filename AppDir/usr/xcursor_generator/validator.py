REQUIRED_CURSORS = [
    "left_ptr",
    "pointer",
    "text",
    "wait",
]


def validate_assets(assets):
    """
    Checks if the theme has the minimum required cursor types.
    Returns (success, missing_list)
    """

    found = set()

    for asset in assets:
        if isinstance(asset, tuple):
            found.add(asset[1])
        elif isinstance(asset, dict):
            found.add(asset.get("type"))

    missing = []

    for cursor in REQUIRED_CURSORS:
        if cursor not in found:
            missing.append(cursor)

    return len(missing) == 0, missing
