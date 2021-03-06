import xml.etree.cElementTree as ET
from pprint import pprint
import re
import codecs
import json
from collections import defaultdict

OSMFILE = "denver-boulder_colorado.osm"

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
POS = ["lat", "lon"]

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Circle", "Way", "Broadway", "Colfax"]

mapping = { "St": "Street",
            "St.": "Street",
            "Ave" : "Avenue",
            "Ave." : "Avenue",
            "Rd" : "Road",
            "Rd." : "Road",
            "Blvd" : "Boulevard",
            "Blvd." : "Boulevard",
            "Cir" : "Circle",
            "Cir." : "Circle",
            "Ct" : "Court",
            "Ct." : "Court",
            "Dr" : "Drive",
            "Dr." : "Drive",
            "Pl" : "Place",
            "Pl." : "Place",
            }

###########################################################################################################
#This section audits the street value. The function see_st_types prints a list of street
#entries that are possible canadites for editing. Values can be added to the expected list
#if an entry is deemed acceptable. If not, a key value pair can be added to the mapping
#dictionary which will be used to make edits in the cleaning section of the code.
###########################################################################################################

#finding values of addr:street
def is_street_name(element):
    return (element.attrib['k'] == "addr:street")
#using a regular expression to pull out the last word in the entry, check it against the 
#expected list, then add it to the street types dictionary if it is not in expected 
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
    
#opens and iterates through file 
def audit(osmfile):
    with open(osmfile, "r") as osm_file:
        street_types = defaultdict(set)
        for event, element in ET.iterparse(osm_file, events=("start",)):
            if element.tag == "node" or element.tag == "way":
                for tag in element.iter("tag"):
                    if is_street_name(tag):
                        audit_street_type(street_types, tag.attrib['v'])

    return street_types

            
def see_st_types():
    st_types = audit(OSMFILE)
    pprint(dict(st_types))

#see_st_types()

###########################################################################################################
#This part of the program does the actual cleaning
###########################################################################################################

#edits the values of addr:street using the mapping dictionary    
def update_name(name, mapping):
    name = name.strip()
    m = street_type_re.search(name)
    street_type = m.group()
    if street_type in mapping.keys():
        #print 'Before: ' , name
        if m not in expected:
            name = re.sub(m.group(), mapping[m.group()], name)
        #print 'After: ', name
    return name

 
def shape_element(element):
    node = {}
    created = {}
    address = {}
    gnis = {}
    pos = [0,0]
    node_refs = []
    if element.tag == "node" or element.tag == "way" or element.tag == "relation" :
 
        #for each element, element.attrib creates a dictionary of attribute:value (key:value) pairs
        #adding .key specifies that the for statement only addresses keys in the dictionary
        #the variable a is a placeholder that will stand for the attribute that the for statement is cycling through  
        for a in element.attrib.keys():
            if a in CREATED:
                #insert key:value pair into created dictionary 
                created[a] = element.attrib[a]
                #print created
            #assigns pos[0] to lat and pos[1] to lon unless an error is thrown
            #if an error is thrown the attribute value is printed along with the type
            elif a in POS:
                if a == 'lat':
                    try:
                        pos[0] = float(element.attrib[a])
                    except:
                        print element.attrib[a]
                        print "The lon and lat values cannot be converted to float:", type(a)
                else:
                    try:
                        pos[1] = float(element.attrib[a])
                    except:
                        print element.attrib[a]
                        print "The lon and lat values cannot be converted to float:", type(a)
            else:
                node[a] = element.get(a) 

        for subtag in element:
            #used for an attribute that will replaced in this function
            #other variables could be listed here as new2, new3, etc.
            new = subtag.get('k')
            if subtag.tag == 'tag':
                # if tag has problematic characters, ignore
                if re.search(problemchars, subtag.get('k')):
                    continue
                # if tag has the structure word:word:word it is passed over
                elif re.search(r'\w+:\w+:\w+', subtag.get('k')):
                    pass
                #alternative method to above satement which will take care of more than two colons:
                #addrk = subtag.attrib['k'].split(':')
                #if len(addrk) > 2:
                    #pass
                # if tag starts with tiger:, pass
                elif subtag.get('k').startswith('tiger:'):
                    pass 
                # if tag starts with addr:, add to dictionary "address"
                elif subtag.get('k').startswith('addr:'):
                    #print subtag.get('k')
                    #print subtag.get('v')
                    key = subtag.get('k')[5:]
                    if  key == "street":
                        #print subtag.get('v')
                        address[key] = update_name(subtag.get('v'), mapping)
                        #print "Edited:", address
                    else: 
                        address[key] = subtag.get('v')
                        #print "Unchanged:", address
                #for all k attributes thta start with gnis, the key:value pairs will 
                #be added to a gnis dictionary 
                elif subtag.get('k').startswith('gnis:'):
                    gkey = subtag.get('k')[5:]
                    gnis[gkey] = subtag.get('v')
                    #print gnis
                #if a 'v' attribute is no or yes, the key:value pair will not be added
                elif subtag.get('v') == 'no' or subtag.get('v') == 'yes':
                    pass
                #replacing an attribute name for another
                elif new == 'shop':
                    new = 'amenity'
                else: node[subtag.get('k')] = subtag.get('v')
            #add ref attributes to a the node_refs dictionary
            if subtag.tag == 'nd':
                    node_refs.append(subtag.get('ref'))
                
    node['type'] = element.tag 
    if created:
        node['created'] = created
    if address:
        node['address'] = address
    if gnis:
        node['gnis'] = gnis
    if node_refs:
        node['node_refs'] = node_refs
    if pos != [0,0]:
       node['pos'] = pos



    if node:
        return node
    else:
        return None


###########################################################################################################
#The cleaned data is converted into a json file in this function
###########################################################################################################

def process_map(file_in, pretty = False):
    i=0
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            print i
            i += 1
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data
    
def main_test():
    data = process_map(OSMFILE, False)
    #print(data)
    print len(data)
    print 'Map processed'

main_test()



