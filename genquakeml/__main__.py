#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Updated on Tue Aug  3 10:34:00 2021
@author: sheecegardezi

Quakeml Generator uses the Obspy framework to create, fill and write a new event to
a quakeml file.  Data to be written to a quakeml file is passed to the program as a
.txt file. Instructions and examples for formatting the .txt file for proper parsing
are in 'README.md'. For licensing and disclaimers see LICENSE.md and DISCLAIMER.md
"""
import argparse
import configparser
import time
import logging
import os
import json
from pathlib import Path
from utils import txt2dictionary, lowercaseInput, updateDictionary, depthToMeters, generateCreationInfo, generateOrigin, generateMagnitude, generateEvent
import obspy


def validate_file(f):
    if not os.path.isfile(f):
        raise argparse.ArgumentTypeError("{0} does not exist".format(f))
    return f


def main():

    parser = argparse.ArgumentParser(description='Download GA QuakeML Seismologic Data')
    parser.add_argument("-i", "--input", type=validate_file, help="input Json file", metavar="FILE", required=True)
    parser.add_argument("-o", "--output", type=validate_file, help="output QuakeML file", metavar="FILE", required=True)
    parser.add_argument("-l", "--log", type=str.upper, default="INFO", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level", required=False)

    args = parser.parse_args()

    if args.logLevel:
        logging.basicConfig(level=getattr(logging, args.logLevel))

    logging.info("Running GenQuakeML")
    read_file = open(args.input, "rb")
    input_data = json.load(read_file)
    read_file.close()

    data, output_filename = txt2dictionary()  # import file to python dictionary and get output filename
    lowercaseInput(data)  # make case-sensitive input lowercase
    updateDictionary(data)  # generate calculated fields
    depthToMeters(data)

    # Generate quakeml with obspy
    magnitudes, origins = [], []  # lists for magnitudes and origins
    creation_info = generateCreationInfo(data)  # create creation_info object
    origin = generateOrigin(data, creation_info)  # create origin object
    origins.append(origin)
    magnitude = generateMagnitude(data, creation_info, origin)  # create magnitude object
    magnitudes.append(magnitude)
    event = generateEvent(data, creation_info, origins, magnitudes)  # create event object

    # Add ANSS specific attributes
    extra = {'eventsource': {'value': data['eventsource'],
                             'type': 'attribute',
                             'namespace': 'http://anss.org/xmlns/catalog/0.1'},
             'dataid': {'value': data['dataid'],
                        'type': 'attribute',
                        'namespace': 'http://anss.org/xmlns/catalog/0.1'},
             'eventid': {'value': data['eventid'],
                         'type': 'attribute',
                         'namespace': 'http://anss.org/xmlns/catalog/0.1'},
             'datasource': {'value': data['datasource'],
                            'type': 'attribute',
                            'namespace': 'http://anss.org/xmlns/catalog/0.1'}}
    event.extra = extra  # add attributes to event
    catalog = obspy.core.event.Catalog(events=[event], resource_id=data['epPid'])  # create catalog object

    # Write event if new or updated using obspy write
    catalog.write(output_filename, format='QUAKEML',
                  nsmap={'catalog': 'https://anss.org/xmlns/catalog/0.1'})

    print("file was exported to: " + output_filename)



if __name__ == '__main__':
    main()
