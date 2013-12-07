# Used to enter data in the database, based on the files given

from Models.models import Trail, Panorama, Link, PointOfInterest
from os import walk, path
from io import open, IOBase

class InfoComp(object):
	def __init__(self, Lat, Lng, Name, Heading):
		self.Lat = Lat
		self.Lng = Lng
		self.Name = Name
		self.Heading = Heading

def insertData(GPS_Coords, Pano_Dir, Headings, Forw_Headings, Trail_Name, Entry_Pano, Image_Width, Tile_Width):
	if not path.exists(Pano_Dir):
		print "Pano Dir doesn't exists"
		return 

	try:
		gps_file = open(GPS_Coords)
		headings_file = open(Headings)
		forw_headings_file = open(Forw_Headings)
	except IOError:
		print "Failed to open a file."
		return

	(_, dirs, _) = walk(Pano_Dir).next()

	comp = []

	coords = gps_file.readlines()
	headings = headings_file.readlines()
	forw_headings = forw_headings_file.readlines()

	if(Entry_Pano == 'True'):
		if((len(coords) - 1) == len(headings) == len(forw_headings)):
			coord_str = coords[0].split(", ")
			comp.append(InfoComp(float(coord_str[0]), float(coord_str[1]), "_entryPano", 0))
			for i in range(len(headings)):
				coord_str = coords[i + 1].split(", ")
				comp.append(InfoComp(float(coord_str[0]), float(coord_str[1]), dirs[i], int(headings[i])))

		else:
			print "File line lengths are not the same"
			return
	else:
		if(len(coords) == len(headings) == len(forw_headings)):
			for i in range(len(headings)):
				coord_str = coords[i].split(", ")
				comp.append(InfoComp(float(coord_str[0]), float(coord_str[1]), dirs[i], int(headings[i])))
		else:
			print "File line lengths are not the same"
			return

	Trail(Name=Trail_Name).save()
	trail_id = Trail.objects.get(Name=Trail_Name).id

	for idx,c in enumerate(comp):
		Panorama(TrailId=trail_id,
			     Name=c.Name,
			     Description=Trail_Name + " Panorama " + str(idx + 1),
			     PanoNumber=idx,
			     LocationLat=c.Lat,
			     LocationLng=c.Lng,
			     TileWidth=Tile_Width,
			     WorldWidth=Image_Width,
			     Heading=c.Heading,
			     InitialHeading=int(forw_headings[idx - 1])).save()

	panos = Panorama.objects.all().order_by('PanoNumber')

	offset = 0
	# Links for entry panos if needed
	if(Entry_Pano == 'True'):
		# Entry pano into custom area
		Link(PanoId=panos[offset].id,
			 TrailId=trail_id,
			 Heading=int(forw_headings[offset]),
			 Description="Into " + Trail_Name,
			 PanoName=panos[offset + 1].Name,
			 IsEntryPano='True').save()
		offset += 1
		# Out of custom area
		Link(PanoId=panos[offset].id,
			 TrailId=trail_id,
			 Heading=(int(forw_headings[offset]) if ((int(forw_headings[offset] - 180) > 0)) else (360 - (forw_headings[offset] - 180))),
			 Description="Out of " + Trail_Name,
			 PanoName=panos[offset - 1].Name,
			 IsEntryPano='False').save()

	# First (possibly lone) link for first custom pano
	Link(PanoId=panos[offset].id,
		 TrailId=trail_id,
		 Heading=int(forw_headings[offset]),
		 Description='Forward',
		 PanoName=panos[offset].Name,
		 IsEntryPano='False').save()

	offset += 1

	while offset < (len(comp) - 1):
		# Backwards link
		Link(PanoId=panos[offset].id,
			 TrailId=trail_id,
			 Heading=int(forw_headings[offset]),
			 Description='Backwards',
			 PanoName=panos[offset + 1].Name,
			 IsEntryPano='True').save()

		# Forwards link
		Link(PanoId=panos[offset].id,
		 TrailId=trail_id,
		 Heading=int(forw_headings[offset]),
		 Description='Forward',
		 PanoName=panos[offset].Name,
		 IsEntryPano='False').save()

		offset += 1

	# Final backwards link
	Link(PanoId=panos[offset].id,
			 TrailId=trail_id,
			 Heading=int(forw_headings[offset]),
			 Description='Backwards',
			 PanoName=panos[offset + 1].Name,
			 IsEntryPano='True').save()

	# Clean up
	gps_file.close()
	headings_file.close()
	forw_headings_file.close()

	
def safeInsertData(GPS_Coords, Pano_Dir, Headings, Forw_Headings, Trail_Name, Entry_Pano, Image_Width, Tile_Width):
	if not os.exists(Pano_Dir):
		print "Pano Dir doesn't exists"
		return

	try:
		gps_file = open(GPS_Coords)
		headings_file = open(Headings)
		forw_headings_file = open(Forw_Headings)
	except IOError:
		print "Failed to open a file."
		return

def clearDatabaseAndInsertData(GPS_Coords, Pano_Dir, Headings, Forw_Headings, Trail_Name, Entry_Pano, Image_Width, Tile_Width):
	if not os.exists(Pano_Dir):
		print "Pano Dir doesn't exists. Data has not been deleted."
		return

	try:
		gps_file = open(GPS_Coords)
		headings_file = open(Headings)
		forw_headings_file = open(Forw_Headings)
	except IOError:
		print "Failed to open a file. Data hsa not been deleted."
		return
	else:
		gps_file.close()
		headings_file.close()
		forw_headings_file.close()

	models.PointOfInterest.objects.all().delete()
	models.Link.objects.all().delete()
	models.Panorama.objects.all().delete()
	models.Trail.objects.all().delete()

	insertData(GPS_Coords, Pano_Dir, Headings, Forw_Headings, Trail_Name, Entry_Pano, Image_Width, Tile_Width)
