from typing import List, NamedTuple
import sys

class Location(NamedTuple):
	"""Represents a lat,long coordinate pair.

	Latitude and longitude should be expressed in floating-point
	degrees.
	"""
	latitude: float
	longitude: float

class WeightedLine(NamedTuple):
	start: Location
	end: Location
	weight: int

def read_segments() -> List[WeightedLine]:
	"""Reads a list of weighted route segments from stdin.

	There should be one segment per line, expressed in the format
	"start_lat, start_lon, end_lat, end_lon, weight".
	"""
	segments: List[WeightedLine] = []
	for line in sys.stdin:
		# Each line represents a weighted path segment on the map.
		try:
			start_lat, start_lon, end_lat, end_lon, wt = line.split(',')
			start = Location(latitude = float(start_lat),
			                 longitude = float(start_lon))
			end = Location(latitude = float(end_lat),
			               longitude = float(end_lon))
			segment = WeightedLine(start, end, int(wt))
		except ValueError:
			pass
		else:
			segments.append(segment)
	return segments
