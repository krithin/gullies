#! /usr/bin/env python

from typing import List
import sys
import random
import osmium

class RandomNodeSelector(osmium.SimpleHandler):
	"""Picks 'node_count' uniformly randomly selected OSM nodes."""
	def __init__(self, node_count: int) -> None:
		osmium.SimpleHandler.__init__(self)
		self.node_count = node_count
		self.node_list: List[osmium.osm.Node] = []
		self.node_index = 0  # indexes nodes while iterating over them

	def node(self, n):
		self.node_index += 1
		if len(self.node_list) < self.node_count:
			# We're still looking at the initial few nodes
			self.node_list.append(n)
		else:
			# We have to pick the ith element with probability n/i
			threshold = self.node_count / float(self.node_index)
			if random.random() < threshold:
				# We do want this element. Kick out one of the existing
				# ones at random:
				self.node_list[random.randrange(self.node_count)] = n

if __name__ == '__main__':
	"""Picks out NUM_NODES randomly selected nodes from the given OSM
	dataset and prints their lat,long coordinates.
	"""
	NUM_NODES = 10
	if not len(sys.argv) == 2:
		sys.exit('Usage: %s myregion.osm.pbf' % sys.argv[0])

	random_handler = RandomNodeSelector(NUM_NODES)
	random_handler.apply_file(sys.argv[1])
	nodes = random_handler.node_list
	
	print(nodes)
