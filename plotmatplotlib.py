#! /usr/bin/env python

import sys
import math

from mpl_toolkits.basemap import Basemap
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

	fig = plt.figure(figsize=(30,30))
	ax = fig.add_subplot(111)
	ax.axes.set_aspect('equal', 'box')
	# Use an Albers equal-area projection for the US
	m = Basemap(projection='cyl',
	    # Standard parallels
	    #lat_1=1.26, lat_2=1.44,
	    # Central point
	    #lat_0=1.35, lon_0=103.81,
	    # Coordinates of the corners of the map.
	    #llcrnrlon=103.5, llcrnrlat=1.2,
	    #urcrnrlon=104.1, urcrnrlat=1.5,
	    # Don't read in any basemap boundary shapefiles.
	    resolution=None)
	ax.text(0.99, 0.01,
	    'github.com/krithin/gullies. '
	    'Data © OpenStreetMap contributors. '
	    'Routing by OSRM.',
	    verticalalignment = 'bottom', horizontalalignment = 'right',
	    transform = ax.transAxes, fontsize = 12)
	print('About to plot %d segments' % len(segments))
	for s in segments:
		startx, starty = m(s.start.longitude, s.start.latitude)
		endx, endy = m(s.end.longitude, s.end.latitude)
		plt.plot([startx, endx], [starty, endy],
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
