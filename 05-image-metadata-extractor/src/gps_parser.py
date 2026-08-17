from __future__ import annotations
def _dms_to_decimal(values) -> float:
    """
    EXIF stores GPS coordinates as three Ratio objects: degrees,
    minutes, seconds (e.g. 48/1, 51/1, 24123/1000). This converts
    that to a single decimal-degree float, which is what every
    mapping library actually wants.
    """
    degrees = values[0].num / values[0].den
    minutes = values[1].num / values[1].den
    seconds = values[2].num / values[2].den
    return degrees + (minutes / 60.0) + (seconds / 3600.0)


def get_gps_coordinates(tags: dict) -> tuple[float, float] | None:
    """
    Returns (latitude, longitude) as decimal degrees, or None if the
    image has no embedded GPS data at all -- most images taken with
    location services off won't have these tags present.
    """
    lat_tag = tags.get("GPS GPSLatitude")
    lat_ref = tags.get("GPS GPSLatitudeRef")
    lon_tag = tags.get("GPS GPSLongitude")
    lon_ref = tags.get("GPS GPSLongitudeRef")

    if lat_tag is None or lon_tag is None:
        return None

    lat = _dms_to_decimal(lat_tag.values)
    lon = _dms_to_decimal(lon_tag.values)

    # South and West are negative in decimal-degree convention
    if lat_ref is not None and str(lat_ref) == "S":
        lat = -lat
    if lon_ref is not None and str(lon_ref) == "W":
        lon = -lon

    return (lat, lon)