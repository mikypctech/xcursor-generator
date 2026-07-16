# xcursor_generator/autogenerator.py

KEYWORD_MAP = {
    "bottom_right": "bottom_right_corner",
    "bottom_left": "bottom_left_corner",
    "top_right": "top_right_corner",
    "top_left": "top_left_corner",

    "nwse": "size_bdiag",
    "nesw": "size_fdiag",

    "bdiag": "size_bdiag",
    "fdiag": "size_fdiag",

    "pointer": "pointer",
    "hand": "pointer",
    "link": "pointer",

    "arrow": "left_ptr",
    "default": "left_ptr",

    "busy": "busy",
    "wait": "wait",
    "progress": "wait",

    "text": "text",
    "ibeam": "text",

    "cross": "crosshair",

    "move": "move",
    "fleur": "move",

    "help": "help",
    "question": "help",

    "forbidden": "forbidden",
    "not-allowed": "forbidden",

    "horizontal": "size_hor",
    "vertical": "size_ver",
}


def get_best_match(filename):
    name = filename.lower()

    for key, value in KEYWORD_MAP.items():
        if key in name:
            return value

    return "left_ptr"
