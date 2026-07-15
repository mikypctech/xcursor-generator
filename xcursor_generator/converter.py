# xcursor_generator/converter.py
import io
import os
from PIL import Image  # <-- Make sure this line is here at the very top!
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

def get_preview_pixmap(file_path):
    """Generates a QPixmap preview for PNG, CUR, or ANI files."""
    try:
        # 1. Standard PNG
        if file_path.lower().endswith('.png'):
            pixmap = QPixmap(file_path)
            return pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        # 2. Windows .cur and .ani files
        elif file_path.lower().endswith(('.cur', '.ani')):
            from win2xcur.parser import open_blob

            with open(file_path, 'rb') as f:
                blob = f.read()

            parser = open_blob(blob)

            if parser and parser.frames:
                first_frame = parser.frames[0]
                if first_frame.images:
                    best_image = first_frame.images[0]

                    byte_arr = io.BytesIO()
                    best_image.image.save(byte_arr)
                    byte_data = byte_arr.getvalue()

                    pixmap = QPixmap()
                    pixmap.loadFromData(byte_data)
                    return pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    except Exception as e:
        print(f"Could not load preview for {file_path}: {e}")

    return None

def convert_to_xcursor(src_path, target_file_path):
    """Converts a source file to a Linux XCursor file using win2xcur's to_x11 helper."""
    from win2xcur.parser import open_blob
    from win2xcur.writer import to_x11  # <-- Import the direct helper function!

    if src_path.lower().endswith('.png'):
        from win2xcur.common import CursorImage, Frame
        img = Image.open(src_path)
        cursor_img = CursorImage(img, (0, 0))  # Default hotspot (0, 0)
        frame = Frame([cursor_img])
        frames = [frame]

    elif src_path.lower().endswith(('.cur', '.ani')):
        with open(src_path, "rb") as f:
            blob = f.read()

        parser = open_blob(blob)
        frames = parser.frames

    # Convert the frames to XCursor bytes and write them out
    xcursor_bytes = to_x11(frames)
    with open(target_file_path, "wb") as f:
        f.write(xcursor_bytes)
