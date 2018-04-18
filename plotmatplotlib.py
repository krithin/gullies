#! /usr/bin/env python

from typing import DefaultDict, Iterable, List, Set, NamedTuple
from collections import defaultdict
import sys
import math

import matplotlib.pyplot as plt

import common

def length_squared(segment: common.WeightedLine) -> float:
	""" Returns the approximate square of the segment's length.

	We approximate this with an appropriately scaled rectangular
	projection."""
	# TODO: deal with things that cross longitude 180 deg or poles.
	EARTH_RADIUS_SQ = 6371.0 * 6371.0 # km * km
	start: common.Location = segment.start
	end: common.Location = segment.end
	delta_lat = math.radians(end.latitude - start.latitude)
	mean_lat = math.radians((end.latitude + start.latitude) / 2)
	delta_lon = math.radians(end.longitude - start.longitude)
	scaled_delta_lon = delta_lon * math.cos(mean_lat)
	return (EARTH_RADIUS_SQ * (
	    delta_lat * delta_lat + scaled_delta_lon * scaled_delta_lon))

def simplify_segments(segments: Iterable[common.WeightedLine]) -> Set[common.WeightedLine]:
	"""Simplifies the list of segments to make it easier to render.

	We want to merge route segments that are under 1km long with
	adjacent segments so there's less to render. However, we will not
	merge segments in a way that moves points where routes branch off
	from each other."""
	# A pair of segments can be concatenated if they share an endpoint
	# and have the same weight (which means their shared endpoint must
	# not have been a branching point), and one of them is under 1km
	# long.
	# This relies on the fact that shortest-path routes never intersect!
	MIN_SQ_LENGTH = 1  # (Min length in km) ^ 2.
	# Two different indexes into the set of segments that are under the
	# minimum plotting length; by their start and end points.
	mergeable_segments_by_start: DefaultDict[
	    common.Location, Set[common.WeightedLine]] = defaultdict(set)
	mergeable_segments_by_end: DefaultDict[
	    common.Location, Set[common.WeightedLine]] = defaultdict(set)
	plottable_segments: Set[common.WeightedLine] = set()
	i = 0
	for s in segments:
		i += 1
		if length_squared(s) > MIN_SQ_LENGTH:
			# s is already long enough by itself that we can plot it.
			plottable_segments.add(s)
		else:
			# Check if we can merge s with some other short segment. In
			# general it may be merged on both the start and end.
			segments_to_remove: List[common.WeightedLine] = []
			for m in mergeable_segments_by_start[s.end]:
				if m.weight == s.weight:
					print('merged start %d %s %s' % (i, repr(m), repr(s)))
					segments_to_remove.append(m)
					s = common.WeightedLine(s.start, m.end, s.weight)
					if length_squared(s) > MIN_SQ_LENGTH:
						plottable_segments.add(s)
					break
			for m in mergeable_segments_by_end[s.start]:
				if m.weight == s.weight:
					segments_to_remove.append(m)
					s = common.WeightedLine(m.start, s.end, s.weight)
					if length_squared(s) > MIN_SQ_LENGTH:
						plottable_segments.add(s)
					break
			for m in segments_to_remove:
				if m.start == common.Location(latitude=40.578471, longitude=-73.989452):
					print(repr(mergeable_segments_by_start[m.start]))
					print(repr(m.start))
					print(repr(mergeable_segments_by_end[m.end]))
					print(repr(m.end))
					print(i)
				mergeable_segments_by_start[m.start].remove(m)
				mergeable_segments_by_end[m.end].remove(m)
			if s not in plottable_segments:
				mergeable_segments_by_start[s.start].add(s)
				mergeable_segments_by_end[s.end].add(s)

	# Unpack all the remaining unmerged segments into a single set
	unmerged_segments = set.union(*mergeable_segments_by_start.values())
	print('%d segments above minimum length, %d below' % (
	    len(plottable_segments), len(unmerged_segments)))
	return plottable_segments.union(unmerged_segments)

if __name__ == '__main__':
	"""Reads a list of route segment weights (expressed in the format
	start_lat, start_lon, end_lat, end_lon, weight) from stdin and
	plots that on a map.
	"""
	if not len(sys.argv) == 2:
		sys.exit('Usage: %s output_filename.png' % sys.argv[0])

	raw_segments = common.read_segments()
	print('About to simplify %d raw segments.' % len(raw_segments))
	segments: Set[common.WeightedLine] = simplify_segments(raw_segments)
	count = 0

	fig = plt.figure(figsize=(24,18), dpi=400)
	ax = fig.add_subplot(111)
	ax.text(0.99, 0.01,
	    'github.com/krithin. Data © OpenStreetMap contributors.',
	    verticalalignment = 'bottom', horizontalalignment = 'right',
	    transform = ax.transAxes, fontsize = 12)
	print('About to plot %d segments' % len(segments))
	for s in segments:
		plt.plot([s.start.longitude, s.end.longitude],
		         [s.start.latitude, s.end.latitude],
		         color = 'k', linestyle = '-', solid_capstyle = 'round',
		         linewidth = math.sqrt(s.weight) / 2)
		count += 1
		if (count % 5000 == 0):
			print('Plotted %d of %d segments' % (count, len(segments)))
	print('Saving figure')
	plt.savefig(sys.argv[1])
