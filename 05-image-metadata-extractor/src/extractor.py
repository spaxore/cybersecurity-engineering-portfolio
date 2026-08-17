from __future__ import annotations

import exifread


def read_exif_tags(image_path: str) -> dict:
    """
    Returns the raw EXIF tags from an image, keyed by tag name
    (e.g. "GPS GPSLatitude", "Image Model").

    Kept deliberately "raw" (exifread's IfdTag objects, not strings) --
    gps_parser.py needs the underlying Ratio numbers to do math on,
    and a display/report layer can stringify these separately later.
    """
    with open(image_path, "rb") as f:
        return exifread.process_file(f, details=False)