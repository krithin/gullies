#! /usr/bin/env python

from typing import List, Any, Iterable
import sys
import requests

class OSRMException(Exception):
	pass

class Location():
	def __init__(self, latitude: float, longitude: float) -> None:
		self.latitude = latitude
		self.longitude = longitude

class OSRMRouteNodesClient():
	def __init__(self, osrm_server_url: str,
	             default_starting_location: Location) -> None:
		self._start = default_starting_location
		self._osrm_server_url = self._sanitize_url(osrm_server_url)

	# TODO: Use a real URL library instead.
	def _sanitize_url(self, url: str) -> str:
		if not ('http://' in url or 'https://' in url):
			raise ValueError("OSRM server url should begin with 'http'")
		if url[-1] == '/':
			return url[:-1]
		return url

	def route_to_destination(self, destination: Location) -> List[int]:
		"""Gets the route to the destination as a list of OSM node IDs.

		This queries OSRM to get a route from the default starting
		location to the destination. It returns a list of OSM node IDs
		corresponding to the route, excluding the start and end points.
		"""
		api_prefix = '/route/v1/driving/'
		# Just get the list of intermediate OSM nodes.
		options = {
			'steps': 'false',
			'overview': 'false',
			'annotations': 'nodes',
		}

		# OSRM expects longitude,latitude for coordinates.
		start_end_coordinate_string = '%f,%f;%f,%f' % (
			self._start.longitude, self._start.latitude,
			destination.longitude, destination.latitude)
		request_url = '%s%s%s' % (self._osrm_server_url, api_prefix,
								  start_end_coordinate_string)

		r = requests.get(request_url, params=options)
		r.raise_for_status()
		response = r.json()

		if not response['code'] == 'Ok':
			raise OSRMException('OSRM returned non-Ok status code: %s',
								response['code'])

		if not len(response['routes']) == 1:
			raise OSRMException('Expected only one route, not %d',
								len(response['routes']))

		route = response['routes'][0]

		# Quick check for common error cases
		if route['distance'] == 0 or route['duration'] == 0:
			raise OSRMException('Route too short to be true.')

		return route['legs'][0]['annotation']['nodes']

	def route_to_destinations(self, destinations: Iterable[Location]) -> List[List[int]]:
		# This could probably be done with the table service instead.
		# https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md#table-service
		MAX_ROUTE_COUNT = 1000
		routes = []
		for destination in destinations:
			routes.append(self.route_to_destination(destination))
			if len(routes) == MAX_ROUTE_COUNT:
				break
		return routes

if __name__ == '__main__':
	if not len(sys.argv) == 2:
		sys.exit('Usage: %s http://my-osrm-server.cc[:port]')

	# Let's start at the empire state building in New York
	start_location = Location(40.748433, -73.985656)
	osrm_client = OSRMRouteNodesClient(sys.argv[1], start_location)

	# Read the lat,long coords of the destination points from stdin
	destinations: List[Location] = []
	for line in sys.stdin:
		try:
			latitude,longitude = line.split(',')
			destination = Location(float(latitude), float(longitude))
		except ValueError:
			pass
		else:
			destinations.append(destination)
	for route in osrm_client.route_to_destinations(destinations):
		print(repr(route)[1:-1])  # Remove the []-brackets around the list
