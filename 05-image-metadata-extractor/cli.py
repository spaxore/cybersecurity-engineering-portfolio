from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from extractor import read_exif_tags
from gps_parser import get_gps_coordinates
from map_renderer import render_location


def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <path-to-image.jpg>")
        sys.exit(1)

    image_path = sys.argv[1]

    if not os.path.isfile(image_path):
        print(f"File not found: {image_path}")
        sys.exit(1)

    tags = read_exif_tags(image_path)
    coordinates = get_gps_coordinates(tags)

    if coordinates is None:
        print("No GPS data found in this image.")
        print("(Either location services were off, or GPS EXIF was stripped somewhere along the way.)")
        sys.exit(0)

    lat, lon = coordinates
    print(f"GPS coordinates found: {lat:.6f}, {lon:.6f}")

    output_file = "location_map.html"
    render_location(lat, lon, output_file)
    print(f"Map written to {output_file} -- open it in your browser.")


if __name__ == "__main__":
    main()