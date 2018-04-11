#! /usr/bin/env python

from typing import DefaultDict, Dict, Iterable, List, NamedTuple, Set
from collections import defaultdict
import sys
import osmium

class Location(NamedTuple):
	latitude: float
	longitude: float

class NodeLocationHandler(osmium.SimpleHandler):
	"""Gets the locations of the given OSM nodes."""
	def __init__(self, node_ids: Set[int]) -> None:
		osmium.SimpleHandler.__init__(self)
		self.node_ids = node_ids
		self.locations: Dict[int, Location] = {}

	def node(self, n):
		if n.id in self.node_ids:
			self.locations[n.id] = Location(
				latitude=n.location.lat, longitude=n.location.lon)

class RouteSegment(NamedTuple):
	"""Represents a route segment by its start and end node IDs."""
	start: int
	end: int

def collate_segments(routes: Iterable[List[int]]) -> Dict[RouteSegment, int]:
	segment_counts: DefaultDict[RouteSegment, int] = defaultdict(int)
	for route in routes:
		prev_node = route[0]
		for node in route[1:]:
			segment_counts[RouteSegment(prev_node, node)] += 1
			prev_node = node
	return segment_counts

if __name__ == '__main__':
	"""Reads a list of routes (each a list of integer node IDs, one
	route per line) from stdin, maps those to a latitude and longitude
	using the given .osm.pbf extract, collates the route segments and
	prints a count of the number of times each route segment was seen.
	"""
	if not len(sys.argv) == 2:
		sys.exit('Usage: %s myregion.osm.pbf' % sys.argv[0])

	routes: List[List[int]] = []
	for line in sys.stdin:
		# Each line should be a list of nodes
		route_nodes = line.split(',')
		route = [int(node) for node in route_nodes]
		routes.append(route)

	route_segment_counts = collate_segments(routes)

	nodes: Set[int] = set()
	for route_segment in route_segment_counts.keys():
		nodes.add(route_segment.start)
		nodes.add(route_segment.end)

	location_handler = NodeLocationHandler(nodes)
	location_handler.apply_file(sys.argv[1])
	node_locations = location_handler.locations

	for route_segment in route_segment_counts.keys():
		start_loc = node_locations[route_segment.start]
		end_loc = node_locations[route_segment.end]
		weight = route_segment_counts[route_segment]
		print('%f,%f,%f,%f,%d' % (
		  start_loc.latitude, start_loc.longitude,
		  end_loc.latitude, end_loc.longitude, weight))
