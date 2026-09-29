"""Decode the bundled Taiwan Atlas TopoJSON, preserving shared polygon edges."""
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def county_boundaries():
    topology = json.loads((Path(__file__).parent / "assets/counties.topo.json").read_text(encoding="utf-8"))
    transform = topology["transform"]
    arcs = []
    for source in topology["arcs"]:
        x = y = 0
        points = []
        for dx, dy in source:
            x += dx
            y += dy
            points.append([x * transform["scale"][0] + transform["translate"][0],
                           y * transform["scale"][1] + transform["translate"][1]])
        arcs.append(points)

    def ring(indices):
        points = []
        for index in indices:
            part = arcs[index] if index >= 0 else arcs[~index][::-1]
            points.extend(part if not points else part[1:])
        if points and points[0] != points[-1]:
            points.append(points[0])
        return points

    features = []
    for geometry in topology["objects"]["counties"]["geometries"]:
        if geometry["type"] == "Polygon":
            coordinates = [ring(indices) for indices in geometry["arcs"]]
        elif geometry["type"] == "MultiPolygon":
            coordinates = [[ring(indices) for indices in polygon] for polygon in geometry["arcs"]]
        else:
            raise ValueError("Unsupported county geometry")
        features.append(dict(type="Feature", properties={"regionName": geometry["properties"]["COUNTYNAME"].replace("台", "臺")},
                             geometry=dict(type=geometry["type"], coordinates=coordinates)))
    return {"type": "FeatureCollection", "features": features}


def region_from_tooltip(tooltip, regions):
    """Accept only a known county name from map interaction data."""
    if not isinstance(tooltip, str):
        return None
    return next((name for name in regions if name in tooltip), None)
