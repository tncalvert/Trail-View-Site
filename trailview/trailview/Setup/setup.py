# Used to enter data in the database, based on the files given

from django.core.exceptions import ObjectDoesNotExist
from trailview.Models.models import Trail, Panorama, Link, PointOfInterest
from os import walk, path
from io import open
import re

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
	trail = Trail.objects.get(Name=Trail_Name)

	for idx,c in enumerate(comp):
		Panorama(TrailId=trail,
			     Name=c.Name,
			     Description=Trail_Name + " Panorama " + str(idx + 1),
			     PanoNumber=idx,
			     LocationLat=c.Lat,
			     LocationLng=c.Lng,
			     TileWidth=Tile_Width,
			     WorldWidth=Image_Width,
			     ForwardHeading=c.Heading,
			     InitialForwardHeading=int(forw_headings[idx - 1])).save()

	panos = Panorama.objects.all().order_by('PanoNumber')

	offset = 0
	# Links for entry panos if needed
	if(Entry_Pano == 'True'):
		# Entry pano into custom area
		Link(PanoId=panos[offset],
			 TrailId=trail,
			 Heading=int(forw_headings[offset]),
			 Description="Into " + Trail_Name,
			 PanoName=panos[offset + 1].Name,
			 IsEntryPano='True').save()
		offset += 1
		# Out of custom area
		Link(PanoId=panos[offset],
			 TrailId=trail,
			 Heading=((int(forw_headings[offset]) - 180) if ((int(forw_headings[offset]) - 180) >= 0) else (360 + (int(forw_headings[offset]) - 180))),
			 Description="Out of " + Trail_Name,
			 PanoName=panos[offset - 1].Name,
			 IsEntryPano='False').save()

	# First (possibly lone) link for first custom pano
	Link(PanoId=panos[offset],
		 TrailId=trail,
		 Heading=int(forw_headings[offset]),
		 Description='Forward',
		 PanoName=panos[offset + 1].Name,
		 IsEntryPano='False').save()

	offset += 1

	while offset < (len(comp) - 1):
		# Backwards link
		Link(PanoId=panos[offset],
			 TrailId=trail,
			 Heading=((int(forw_headings[offset]) - 180) if ((int(forw_headings[offset]) - 180) >= 0) else (360 + (int(forw_headings[offset]) - 180))),
			 Description='Backwards',
			 PanoName=panos[offset - 1].Name,
			 IsEntryPano='True').save()

		# Forwards link
		Link(PanoId=panos[offset],
		 TrailId=trail,
		 Heading=int(forw_headings[offset]),
		 Description='Forward',
		 PanoName=panos[offset + 1].Name,
		 IsEntryPano='False').save()

		offset += 1

	# Final backwards link
	Link(PanoId=panos[offset],
			 TrailId=trail,
			 Heading=((int(forw_headings[offset]) - 180) if ((int(forw_headings[offset]) - 180) >= 0) else (360 + (int(forw_headings[offset]) - 180))),
			 Description='Backwards',
			 PanoName=panos[offset - 1].Name,
			 IsEntryPano='True').save()

	# Clean up
	gps_file.close()
	headings_file.close()
	forw_headings_file.close()

	
def safeInsertData(GPS_Coords, Pano_Dir, Headings, Forw_Headings, Trail_Name, Entry_Pano, Image_Width, Tile_Width):
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

def clearDatabaseAndInsertData(GPS_Coords, Pano_Dir, Headings, Forw_Headings, Trail_Name, Entry_Pano, Image_Width, Tile_Width):
	if not path.exists(Pano_Dir):
		print "Pano Dir doesn't exists. Data has not been deleted."
		return

	try:
		gps_file = open(GPS_Coords)
		headings_file = open(Headings)
		forw_headings_file = open(Forw_Headings)
	except IOError:
		print "Failed to open a file. Data has not been deleted."
		return
	else:
		gps_file.close()
		headings_file.close()
		forw_headings_file.close()

	PointOfInterest.objects.all().delete()
	Link.objects.all().delete()
	Panorama.objects.all().delete()
	Trail.objects.all().delete()

	insertData(GPS_Coords, Pano_Dir, Headings, Forw_Headings, Trail_Name, Entry_Pano, Image_Width, Tile_Width)

# Reads in a file listing the the points of interest for a trail
def addPoIsForTrail(POI_File):
    try:
        file = open(POI_File)
    except IOError:
        print "Could not open file. Please make sure it exists."
    
    # Matches the format of the information
    reg = re.finditer(r"\{(\d+),\n(\d+),\n('[\w\s,.'\-]*'),\n(\d+),\n(\d+),\n('[\w\s,.'\-]*'|None),\n('[\w\s,.'\-]*'|None),\n('[\w\s,.!'\"\-]*'|None)\}", file.read())

    vals = []

    for r in reg:
        vals.append(r.groups())

    for v in vals:

        try:
            trail = Trail.objects.get(id = int(v[4]))
        except ObjectDoesNotExist:
            continue

        PointOfInterest(StartPanoNum=int(v[0]),
                        EndPanoNum=int(v[1]),
                        TrailId=trail,
                        Name=v[2],
                        PoICategory=int(v[3]),
                        Photo=v[5] if v[5] != 'None' else None,
                        Audio=v[6] if v[6] != 'None' else None,
                        Description=v[7] if v[7] != 'None' else None).save()


# Executes a SQL query to fix links in a specific trail
def fixLinksForTrail(Trail_Name, SQL_Query):
    return ''
