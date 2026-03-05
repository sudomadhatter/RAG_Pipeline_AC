import os
import shutil
from datetime import datetime
from pathlib import Path
import config

def get_timestamp() -> str:
    """Returns YYYYMMDD_HHMMSS for superseded files."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def supersede_file(active_path: Path, superseded_dir: Path) -> Path:
    """
    Moves an active file to the superseded directory, appending a timestamp.
    Example: part91.pdf -> part91_20260227_103000.pdf
    """
    if not active_path.exists():
        return None
    
    timestamp = get_timestamp()
    stem = active_path.stem
    ext = active_path.suffix
    new_name = f"{stem}_{timestamp}{ext}"
    
    # Maintain subfolder structure for library if it exists
    # e.g., library/active/regulations/part91.pdf -> library/superseded/regulations/part91...
    rel_path = active_path.parent.name
    if rel_path in ['regulations', 'handbooks', 'advisory_circulars']:
        dest_dir = superseded_dir / rel_path
        dest_dir.mkdir(parents=True, exist_ok=True)
    else:
        dest_dir = superseded_dir
        
    dest_path = dest_dir / new_name
    shutil.move(str(active_path), str(dest_path))
    return dest_path

def activate_file(new_path: Path, active_dir: Path, superseded_dir: Path) -> Path:
    """
    Moves a file from `new/` to `active/`.
    If it already exists in `active/`, supersede the old one first.
    """
    # Determine proper active destination keeping subfolders if library
    if new_path.parent.name in ['regulations', 'handbooks', 'advisory_circulars']:
        dest_dir = active_dir / new_path.parent.name
        dest_dir.mkdir(parents=True, exist_ok=True)
    else:
        dest_dir = active_dir
        
    dest_path = dest_dir / new_path.name
    
    # Supersede existing file if present
    if dest_path.exists():
        supersede_file(dest_path, superseded_dir)
        
    # Move new -> active
    shutil.move(str(new_path), str(dest_path))
    return dest_path
