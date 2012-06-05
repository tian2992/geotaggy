import sys
import xml.etree.ElementTree as etree
import os

import iso8601

class DataPoint:
	def __repr__(self):
		return "{0} {1} {2}".format(self.longitude, self.latitude, self.altitude)
	
	def __init__(self,coordinate):
		coord_list = coordinate.split(" ")
		if len(coord_list) == 3:
			self.longitude = coord_list[0]
			self.latitude = coord_list[1]
			self.altitude = coord_list[2]
		else:
			print("The coordinate could not be read")
			#TODO: log error due to bad format

if (len(sys.argv) == 2):
	#TODO add support for several input files
	kml_file = sys.argv[1]
else:
	#just for fun...
	kml_file = "/Volumes/TIXPERIA/GPSLogger/20120601125840.kml" # should be first attr
with open(kml_file) as file:
  doc = etree.parse(file)
  root = doc.getroot()

#https://developers.google.com/kml/documentation/kmlreference#gxtrack

track_list = list(root[0][1][0])

coord_list, when_list = list(),list()

for item in track_list:
	if "coord" in item.tag:
		coord_list.append(item)
	elif "when" in item.tag:
		when_list.append(item)
	else:
		pass
		#should log that a wrong element got in there...

proper_date_list = map(lambda x: iso8601.parse_date(x.text),when_list)
proper_coord_list = map(lambda x: DataPoint(x.text), coord_list )
paired_list = zip(proper_date_list,proper_coord_list)

##was supposed to only supports track formats in the following format, otherwise it gets screwed
##<when />
##<gx:coord />
#track_node = root.Document.Placemark.getchildren()[0]
#track_list = track_node.getchildren()
#paired_list = zip(track_list[0::2],track_list[1::2])

import flickrapi

api_key = 'd0eeb7c8614111a56f396e42d3918b77'
api_secret = 'dbf6be8ad6eb72d7'

flickr = flickrapi.FlickrAPI(api_key, api_secret)
flickr.token.path = os.getcwd()+'flickrtokens'

(token, frob) = flickr.get_token_part_one(perms='write')
if not token: raw_input("Press ENTER after you authorized this program")
flickr.get_token_part_two((token, frob))

#more magic
set_list = flickr.photosets_getList().find('photosets').findall('photoset')
print(set_list[0].find("title").text)
set_id = set_list[0].attrib["id"] #TODO: it should be an option as well

photos_in_set = flickr.photosets_getPhotos(photoset_id=set_id, extras="date_taken")[0]
#photos_in_set[0][0].attrib["datetaken"]
timezone = iso8601.iso8601.FixedOffset(-6,0,"GMT-6") #TODO: make this an attribute


for photo in photos_in_set:
     date = iso8601.parse_date(photo.attrib["datetaken"],default_timezone=timezone)
     for date_gps, place_gps in paired_list:
             diff = abs(date - date_gps)

