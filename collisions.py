#!/usr/local/bin/python3
""" Filtering & plotting methods for GEO109 final project
Author: Kelly Sovacool
Email: kellysovacool@uky.edu
Date: 13 Apr. 2018

Usage:
    ./collisions.py <geojson_filename> [--filter] [--plot]

Options:
    -h --help       Display this message
    -f --filter     Filter out fatal & bicycle collisions and write to new geojson files
    -p --plot       Plot a histogram and barplot
"""
import collections
import datetime
import docopt
import json
import plotly

def main(args):
    """ Loads the geojson data downloaded from the UK mapshop and calls the filter and/or plot function.
    If neither flag is included, does absolutely nothing.
    :param args: dictionary from docopt argument parser
    """
    with open(args['<geojson_filename>'], 'r') as file:
        collisions = json.load(file)
    if args['--filter']:
        filter(collisions)
    if args['--plot']:
        plot(collisions)

def filter(collisions):
    """ Filters fatal collisions and collisions involving a bicycle. Writes them to separate geojson files.
    :param collisions: dictionary loaded from geojson file.
    :return: None.
    """
    fatal = collisions.copy()
    fatal['features'] = [collision for collision in collisions['features'] if collision['properties']['KILLED'] > 0]
    with open('fatal_collisions.geojson', 'w') as file:
        json.dump(fatal, file)
    bicycle = collisions.copy()
    bicycle['features'] = [collision for collision in collisions['features'] if collision['properties']['DIRECTIO_1'] == 'COLLISION WITH BICYCLE']
    with open('bicycle_collisions.geojson', 'w') as file:
        json.dump(bicycle, file)

def plot(collisions):
    """ Plot a histogram of collisions over time and barplot of roadways with 50+ collisions.
    :param collisions: dictionary loaded from geojson file.
    :return: None.
    """
    dates = list()
    roads_unfiltered = collections.defaultdict(int)
    for collision in collisions['features']:
        y, m, d = collision['properties']['COLLISIO_1'].split('/')
        dates.append(datetime.datetime(int(y), int(m), int(d)))
        name1 = collision['properties']['INTERSEC_1']
        name2 = collision['properties']['INTERSEC_2']
        alt = collision['properties']['INTERSECTI']
        if name1:
            name = name1 + ' ' + name2 if name2 else name1
        elif alt:
            name = alt
        elif name2:
            name = name2
        else:
            name = None
        if name:
            roads_unfiltered[name] += 1
    roads_filtered = {road: count for road, count in roads_unfiltered.items() if count >= 50}  # only include roadways with 50+ collisions
    # plot the histogram of collisions over time
    plotly.offline.plot(plotly.graph_objs.Figure(data=[plotly.graph_objs.Histogram(x=dates, name='all collisions')], 
                                                 layout=plotly.graph_objs.Layout(title='Lexington Collisions 2004 - 2014', 
                                                                                 xaxis=dict(title='Date'), 
                                                                                 yaxis=dict(title='Count'))), 
                        filename='histogram.html')
    # plot the barplot of collisions on roadways
    plotly.offline.plot(plotly.graph_objs.Figure(data=[plotly.graph_objs.Bar(x=list(sorted(roads_filtered.keys())), 
                                                                             y=[roads_filtered[name] for name in sorted(roads_filtered.keys())])], 
                                                 layout=plotly.graph_objs.Layout(title='Lexington Collisions by Roadway 2004 - 2014', 
                                                                                 xaxis=dict(title='Roadway'), yaxis=dict(title='Count'))), 
                        filename='barplot.html')

if __name__ == "__main__":
    main(docopt.docopt(__doc__))
