#! /usr/bin/env python

import sys
import math

import matplotlib.pyplot as plt

import common

if __name__ == '__main__':
	"""Reads a list of route segment weights (expressed in the format
	start_lat, start_lon, end_lat, end_lon, weight) from stdin and
	plots that on a map.
	"""
	if not len(sys.argv) == 2:
		sys.exit('Usage: %s output_filename.png' % sys.argv[0])

	segments = common.read_segments()
	count = 0

	# Match the figure aspect ratio to the data, assuming we want an
	# equirectangular projection.
	latlongs = [(s.end.latitude, s.end.longitude) for s in segments]
	latitudes, longitudes = zip(*latlongs)
	lat_range = max(latitudes) - min(latitudes)
	lon_range = max(longitudes) - min(longitudes)
	long_side_length = 30.0
	if lat_range > lon_range:
		short_side_length = long_side_length * lon_range / lat_range
		figsize = (short_side_length, long_side_length)
	else:
		short_side_length = long_side_length * lat_range / lon_range
		figsize = (long_side_length, short_side_length)
	fig = plt.figure(figsize=figsize)
	ax = fig.add_subplot(111)
	ax.text(0.99, 0.01,
	    'github.com/krithin/gullies. '
	    'Data © OpenStreetMap contributors. '
	    'Routing by OSRM.',
	    verticalalignment = 'bottom', horizontalalignment = 'right',
	    transform = ax.transAxes, fontsize = 12)
	print('About to plot %d segments' % len(segments))
	for s in segments:
		plt.plot([s.start.longitude, s.end.longitude],
		         [s.start.latitude, s.end.latitude],
		         color = 'k', linestyle = '-', solid_capstyle = 'round',
		         linewidth = math.log1p(s.weight))
		count += 1
		if (count % 5000 == 0):
			print('Plotted %d of %d segments' % (count, len(segments)))
	print('Saving figure')
	plt.axis('off')
	ax.get_xaxis().set_visible(False)
	ax.get_yaxis().set_visible(False)
	plt.savefig(sys.argv[1], bbox_inches='tight', pad_inches=0, dpi=600)
