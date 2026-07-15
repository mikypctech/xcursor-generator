# xcursor_generator/packer.py
import os
import shutil
import tempfile
import tarfile
from xcursor_generator.converter import convert_to_xcursor

# In xcursor_generator/packer.py
MAPPA_ALIAS = {
    "left_ptr": ["default", "arrow", "main", "top_left_arrow"],
    "pointer": ["hand", "hand1", "hand2", "link", "pointing_hand"],
    "wait": ["watch", "progress", "0426c175130060002032000000000000"],
    "busy": ["left_ptr_watch"],
    "text": ["xterm", "ibeam", "text-select"],
    "move": ["fleur", "size_all"],
    "forbidden": ["not-allowed", "crossed_circle"],
    "size_hor": ["sb_h_double_arrow", "col-resize"],
    "size_ver": ["sb_v_double_arrow", "row-resize"],
    "size_fdiag": ["bd_double_arrow"],
    "size_bdiag": ["fd_double_arrow"],
    "help": ["whats_this", "question_arrow"]
}

def pack_theme(save_path, theme_name, author, comment, fallback, assets):
    """
    Builds the theme directory structure, converts files,
    creates symlinks, and tars it up.
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            theme_dir = os.path.join(tmpdir, theme_name)
            cursors_dir = os.path.join(theme_dir, "cursors")
            os.makedirs(cursors_dir, exist_ok=True)

            # 1. Generate index.theme
            index_path = os.path.join(theme_dir, "index.theme")
            with open(index_path, "w", encoding="utf-8") as f:
                f.write("[Icon Theme]\n")
                f.write(f"Name={theme_name}\n")
                f.write(f"Comment={comment if comment else 'Custom cursor theme'}\n")
                if author:
                    f.write(f"Author={author}\n")
                if fallback:
                    f.write(f"Inherits={fallback}\n")

            # 2. Convert and place assets
            for src_path, target_type in assets:
                target_file_path = os.path.join(cursors_dir, target_type)
                convert_to_xcursor(src_path, target_file_path)

                # 3. Create symlinks for compatibility
                if target_type in MAPPA_ALIAS:
                    for alias in MAPPA_ALIAS[target_type]:
                        alias_path = os.path.join(cursors_dir, alias)
                        if os.path.exists(alias_path) or os.path.islink(alias_path):
                            os.remove(alias_path)
                        os.symlink(target_type, alias_path)

            # 4. Create the final tarball
            with tarfile.open(save_path, "w:gz") as tar:
                tar.add(theme_dir, arcname=theme_name)

        return True, None
    except Exception as e:
        return False, str(e)
