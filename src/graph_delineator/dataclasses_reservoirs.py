import networkx as nx
import geopandas as gpd
from shapely.geometry import Point
from dataclasses import dataclass
from typing import Tuple



@dataclass
class DelineationResult:
    """Container for delineation results"""

    graph: nx.DiGraph
    outlet_id: str

    def to_geodataframes(
        self, crs="EPSG:4326"
    ) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        """Export graph to GeoDataFrames for visualization/saving"""
        subbasins = self._export_subbasins(crs)
        nodes = self._export_nodes(crs)
        return subbasins, nodes

    def _export_subbasins(self, crs) -> gpd.GeoDataFrame:
        records = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get("polygon") is not None:
                records.append(
                    {
                        "id": node_id,
                        "geometry": data["polygon"],
                        "area_km2": data.get("area_km2", 0),
                        "uparea_km2": data.get("uparea_km2", 0),
                        "original_comid": data.get("original_comid", None),
                        "node_type": data.get("node_type", "unknown"),
                        "is_gauge": data.get("is_gauge", False),
                        "is_reservoir": data.get("is_reservoir", False),
                        "nextdown": list(self.graph.successors(node_id))[0]
                        if self.graph.out_degree(node_id) > 0
                        else None,
                    }
                )
        return gpd.GeoDataFrame(records, crs=crs) if records else gpd.GeoDataFrame()

    def _export_nodes(self, crs) -> gpd.GeoDataFrame:
        records = []
        for node_id, data in self.graph.nodes(data=True):
            # Determine geometry
            geometry = None
            if "lng" in data and "lat" in data:
                geometry = Point(data["lng"], data["lat"])
            
            if geometry is not None:
                records.append(
                    {
                        "id": node_id,
                        "geometry": geometry,
                        "node_type": data.get("node_type", "unknown"),
                        "lat": data.get("lat", geometry.y),
                        "lng": data.get("lng", geometry.x),
                        "area_km2": data.get("area_km2", 0),
                        "uparea_km2": data.get("uparea_km2", 0),
                        "is_gauge": data.get("is_gauge", False),
                        "is_reservoir": data.get("is_reservoir", False),
                    }
                )
        return gpd.GeoDataFrame(records, crs=crs) if records else gpd.GeoDataFrame()
