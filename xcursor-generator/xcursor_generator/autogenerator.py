# xcursor_generator/autogenerator.py

KEYWORD_MAP = {
    "arrow": "left_ptr", "default": "left_ptr", "pointer": "pointer",
    "hand": "pointer", "link": "pointer", "wait": "wait",
    "progress": "wait", "busy": "wait", "working": "wait",
    "text": "text", "ibeam": "text", "entry": "text",
    "move": "move", "fleur": "move", "cross": "crosshair",
    "help": "help", "question": "help", "forbidden": "forbidden",
    "not-allowed": "forbidden", "no-drop": "forbidden",
    "hor": "size_hor", "h-resize": "size_hor",
    "ver": "size_ver", "v-resize": "size_ver",
    "fdiag": "size_fdiag", "bdiag": "size_bdiag",
    "top": "top_side", "bottom": "bottom_side",
    "left": "left_side", "right": "right_side",
    "corner": "top_left_corner"
}

def get_best_match(filename):
    """Returns a valid cursor type based on keywords, defaulting to 'left_ptr'."""
    name = filename.lower()

    for keyword, cursor_type in KEYWORD_MAP.items():
        if keyword in name:
            return cursor_type

    # Default fallback: If it's not in the map, don't crash,
    # just return 'left_ptr' so the user can see it in the UI and pick the right one.
    return "left_ptr"
