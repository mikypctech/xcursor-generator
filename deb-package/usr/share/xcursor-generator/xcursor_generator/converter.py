# xcursor_generator/converter.py
import io
from PIL import Image
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from xcursor_generator.hotspot import get_default_hotspot
from wand.image import Image as WandImage


def get_preview_pixmap(file_path):
    """Generates a QPixmap preview for PNG, CUR, or ANI files."""
    try:
        if file_path.lower().endswith(".png"):
            pixmap = QPixmap(file_path)
            return pixmap.scaled(
                32,
                32,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        elif file_path.lower().endswith((".cur", ".ani")):
            from win2xcur.parser import open_blob

            with open(file_path, "rb") as f:
                blob = f.read()

            parser = open_blob(blob)

            if parser and parser.frames:
                first_frame = parser.frames[0]
                if first_frame.images:
                    best_image = first_frame.images[0]

                    byte_arr = io.BytesIO()
                    best_image.image.save(byte_arr)

                    pixmap = QPixmap()
                    pixmap.loadFromData(byte_arr.getvalue())

                    return pixmap.scaled(
                        32,
                        32,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )

    except Exception as e:
        print(e)

    return None


def convert_to_xcursor(src_path, target_file_path, hotspot=None):
    """
    Converts PNG/CUR/ANI into an XCursor file.
    hotspot=(x,y) is only used for PNGs.
    """

    from win2xcur.parser import open_blob
    from win2xcur.writer import to_x11

    if src_path.lower().endswith(".png"):
        from win2xcur.cursor import CursorImage, CursorFrame

        img = Image.open(src_path)

        if hotspot is None:
            hotspot = get_default_hotspot(img)

        with WandImage(filename=src_path) as wand_img:

            cursor_img = CursorImage(
                wand_img.sequence[0],
                hotspot,
                img.width
            )

            frames = [
                CursorFrame([cursor_img])
            ]

    else:
        with open(src_path, "rb") as f:
            parser = open_blob(f.read())

        frames = parser.frames

    with open(target_file_path, "wb") as f:
        f.write(to_x11(frames))
