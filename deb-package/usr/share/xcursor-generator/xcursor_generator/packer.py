# xcursor_generator/packer.py
import os
import tarfile
import tempfile

from xcursor_generator.validator import validate_assets
from xcursor_generator.converter import convert_to_xcursor
from xcursor_generator.aliases import ALIASES


def pack_theme(
    save_path,
    theme_name,
    author,
    comment,
    fallback,
    assets,
):

    try:
        valid, missing = validate_assets(assets)

        if not valid:
            print(
                "Warning: missing cursors:",
                ", ".join(missing)
            )
        with tempfile.TemporaryDirectory() as tmpdir:

            theme_dir = os.path.join(tmpdir, theme_name)
            cursors_dir = os.path.join(theme_dir, "cursors")

            os.makedirs(cursors_dir, exist_ok=True)

            with open(
                os.path.join(theme_dir, "index.theme"),
                "w",
                encoding="utf-8",
            ) as f:

                f.write("[Icon Theme]\n")
                f.write(f"Name={theme_name}\n")
                f.write(
                    f"Comment={comment or 'Custom cursor theme'}\n"
                )

                if author:
                    f.write(f"Author={author}\n")

                if fallback:
                    f.write(f"Inherits={fallback}\n")


            generated = set()

            for asset in assets:

                src_path = asset["path"]
                target = asset["type"]
                hotspot = asset.get("hotspot")

                if target in generated:
                    continue

                generated.add(target)

                out = os.path.join(
                    cursors_dir,
                    target
                )

                convert_to_xcursor(
                    src_path,
                    out,
                    hotspot=None if hotspot != "auto" else None
                )

                for alias in ALIASES.get(target, []):

                    alias_path = os.path.join(
                        cursors_dir,
                        alias
                    )

                    if os.path.lexists(alias_path):
                        os.remove(alias_path)

                    os.symlink(
                        target,
                        alias_path
                    )


            with tarfile.open(
                save_path,
                "w:gz"
            ) as tar:

                tar.add(
                    theme_dir,
                    arcname=theme_name
                )


        return True, None


    except Exception as e:
        return False, str(e)
