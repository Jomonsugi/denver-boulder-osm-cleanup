#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "denver-boulder_colorado.osm"  # Replace this with your osm file
SAMPLE_FILE = "denver-boulder_colorado_reduced.osm"


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

# changing the number of enumerations from 500 will result in a smaller or larger file accordingly 
with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every 10th top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % 500 == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')

# used to print out a specified number of lines of the xml file in a readable format
```
from pprint import pprint
for i, element in enumerate(get_element(OSM_FILE)):
    pprint(ET.tostring(element, encoding='utf-8'))
    if i == 1000:
        break
```

