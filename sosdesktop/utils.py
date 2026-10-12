import glob
import os
from typing import List, Tuple

from .constants import Paths, FilePatterns


def human_readable_size(num_bytes: int) -> str:
    step = 1024.0
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < step:
            if unit == "B":
                return f"{num_bytes:.0f} {unit}"
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= step
    return f"{num_bytes:.1f} PB"


def find_sos_reports() -> List[Tuple[str, int]]:
    candidates: List[str] = []
    patterns = [
        os.path.join(Paths.VAR_TMP, FilePatterns.SOS_REPORT_XZ),
        os.path.join(Paths.VAR_TMP, FilePatterns.SOS_REPORT_GZ),
    ]
    for pattern in patterns:
        candidates.extend(glob.glob(pattern))

    unique_paths = sorted(
        set(candidates), key=os.path.getmtime, reverse=True
    )
    results: List[Tuple[str, int]] = []
    for path in unique_paths:
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        results.append((path, size))
    return results
