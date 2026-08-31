from pathlib import Path

from src.data.graph.osm_builder import build_from_osm_xml


def test_osm_xml_importer_builds_bidirectional_roads(tmp_path: Path):
    osm = tmp_path / "sample.osm"
    osm.write_text(
        """<osm><node id="1" lat="0" lon="0"/><node id="2" lat="0" lon="1"/><node id="3" lat="1" lon="1"/><way id="10"><nd ref="1"/><nd ref="2"/><nd ref="3"/><tag k="highway" v="residential"/></way></osm>""",
        encoding="utf-8",
    )
    graph = build_from_osm_xml(osm)
    assert len(graph.nodes) == 3
    assert {edge.target for edge in graph.neighbors("2")} == {"1", "3"}
