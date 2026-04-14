"""Core conversion functions for iliasqc."""

from __future__ import annotations

import zipfile
from pathlib import Path


def txt_to_zip(input_path: str | Path, output_path: str | Path | None = None) -> Path:
    """Convert a txt question file to an Ilias-compatible zip archive.

    Parameters
    ----------
    input_path:
        Path to the input ``.txt`` file containing the questions.
    output_path:
        Destination for the resulting ``.zip`` file.  When *None* the zip is
        placed next to the input file with the same stem.

    Returns
    -------
    Path
        Absolute path of the created zip archive.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path is None:
        output_path = input_path.with_suffix(".zip")
    output_path = Path(output_path)

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(input_path, arcname=input_path.name)

    return output_path.resolve()
