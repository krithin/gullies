#! /usr/bin/env python

from typing import Iterable, DefaultDict, List, Set, NamedTuple
from collections import defaultdict
import sys
import math

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

def simplify_segments(segments: Iterable[common.WeightedLine],
                      min_length: float) -> Set[common.WeightedLine]:
	"""Simplifies the list of segments to make it easier to render.

	We want to merge route segments that are < min_length with
	adjacent segments so there's less to render. However, we will not
	merge segments in a way that moves points where routes branch off
	from each other."""
	# A pair of segments can be concatenated if they share an endpoint
	# and have the same weight (which means their shared endpoint must
	# not have been a branching point), and one of them is under 
	# min_length in length.
	MIN_SQ_LENGTH = min_length * min_length
	# Segments that are under the minimum plotting length, indexed by
	# their end location.
	mergeable_segments_by_end: DefaultDict[
	    common.Location, Set[common.WeightedLine]] = defaultdict(set)
	plottable_segments: Set[common.WeightedLine] = set()
	for s in segments:
		if length_squared(s) > MIN_SQ_LENGTH:
			# s is already long enough by itself that we can plot it.
			plottable_segments.add(s)
		else:
			# Check if we can merge s with some other short segment.
			match_found = False
			for m in mergeable_segments_by_end[s.start]:
				if m.weight == s.weight:
					match_found = True
					s = common.WeightedLine(m.start, s.end, s.weight)
					break
			if match_found:
				mergeable_segments_by_end[m.end].remove(m)
			# Discard zero-length segments out of hand
			if s.start != s.end:
				if length_squared(s) > MIN_SQ_LENGTH:
					plottable_segments.add(s)
				else:
					mergeable_segments_by_end[s.end].add(s)

	# Unpack all the remaining unmerged segments into a single set
	unmerged_segments = set.union(*mergeable_segments_by_end.values())
	print('%d segments above minimum length, %d below' % (
	    len(plottable_segments), len(unmerged_segments)),
	    file=sys.stderr)
	return plottable_segments.union(unmerged_segments)

if __name__ == '__main__':
	""" Simplifies a list of segments read from stdin, writes to stdout.

	This reads a list of route segment weights (expressed in the format
	start_lat, start_lon, end_lat, end_lon, weight) from stdin and
	simplifies them by merging adjacent segments together until they
	reach the given minimum segment length.
	"""
	if not len(sys.argv) == 2:
		sys.exit('Usage: %s min-length' % sys.argv[0])
	min_length = float(sys.argv[1])

	raw_segments = common.read_segments()

	print('About to simplify %d raw segments.' % len(raw_segments),
	      file=sys.stderr)
	segments: Set[common.WeightedLine] = simplify_segments(raw_segments)

	for s in segments:
		print('%f,%f,%f,%f,%d' % (
		  s.start.latitude, s.start.longitude,
		  s.end.latitude, s.end.longitude, s.weight))
