from __future__ import annotations

import folium


def render_location(lat: float, lon: float, output_path: str = "location_map.html") -> None:
    """
    Drops a single marker at (lat, lon) on an interactive map and
    saves it as a standalone HTML file you can open in a browser.
    """
    map_obj = folium.Map(location=[lat, lon], zoom_start=14)
    folium.Marker(
        location=[lat, lon],
        popup=f"{lat:.6f}, {lon:.6f}",
        icon=folium.Icon(color="red", icon="camera"),
    ).add_to(map_obj)
    map_obj.save(output_path)