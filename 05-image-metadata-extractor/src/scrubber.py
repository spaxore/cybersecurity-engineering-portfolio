from __future__ import annotations

from PIL import Image


def scrub_metadata(input_path: str, output_path: str) -> None:
    """
    Saves a copy of the image with all EXIF/metadata stripped.

    Re-creates the image from raw pixel data only (Image.new + putdata)
    rather than just re-saving the original -- Pillow's default save()
    can silently carry some metadata through depending on format, so
    rebuilding from pixels guarantees nothing hidden survives.
    """
    with Image.open(input_path) as img:
        data = list(img.getdata())
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(data)
        clean_img.save(output_path)
