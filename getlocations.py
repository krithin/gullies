#! /usr/bin/env python

from typing import List
import sys
import random
import osmium

import common

class RandomNodeSelector(osmium.SimpleHandler):
	"""Picks 'node_count' uniformly randomly selected OSM nodes."""
	def __init__(self, node_count: int) -> None:
		osmium.SimpleHandler.__init__(self)
		self.node_count = node_count
		self.location_list: List[common.Location] = []
		self.node_index = 0  # indexes nodes while iterating over them

	def _location(self, node: osmium.osm.Node) -> common.Location:
		return common.Location(latitude = node.location.lat,
		                       longitude = node.location.lon)

	def node(self, n):
		self.node_index += 1
		if self.node_index <= self.node_count:
			# We're still looking at the initial few nodes
			self.location_list.append(self._location(n))
		else:
			# We have to pick the ith element with probability n/i
			threshold = self.node_count / float(self.node_index)
			if random.random() < threshold:
				# We do want this element. Kick out one of the existing
				# ones at random:
				evicted_index = random.randrange(self.node_count)
				self.location_list[evicted_index] = self._location(n)

if __name__ == '__main__':
	"""Picks out NUM_NODES randomly selected nodes from the given OSM
	dataset and prints their lat,long coordinates.
	"""
	# TODO: use argparse instead of parsing ordered command line args.
	if not len(sys.argv) == 3:
		sys.exit('Usage: %s myregion.osm.pbf num_nodes' % sys.argv[0])
	try:
		num_nodes = int(sys.argv[2])
	except ValueError:
		sys.exit('Usage: %s myregion.osm.pbf num_nodes' % sys.argv[0])

	random_handler = RandomNodeSelector(num_nodes)
	random_handler.apply_file(sys.argv[1])
	locations = random_handler.location_list
	
	for location in locations:
		print('%f,%f' % (location.latitude, location.longitude))
