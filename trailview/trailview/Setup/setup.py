# Used to enter data in the database, based on the files given

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from trailview.Models.models import Trail, Panorama, Link, PointOfInterest
from os import walk, path
from io import open
from string import strip
import re

class InfoComp(object):
	def __init__(self, Lat, Lng, Name, Heading):
		self.Lat = Lat
		self.Lng = Lng
		self.Name = Name
		self.Heading = Heading

# Inserts data into the database per the files added
# [GPS_Coords] File containing a list of gps coordinates (see waypoints.txt)
# [Pano_Dir] Directory of all folders for panoramas (e.g., trailview/static/panos/Cadillac South Ridge Trail/)
# [Headings] File containing a list of all headings pointing to North in relation to
#            the center of each corresponding panorama
# [Forw_Headings] Files containing a list of all headings pointing forward on the trail in relation
#                 to North as defined by the headings in the previous file
# [Trail_Name] Name for the trail
# [Entry_Pano] 'True' or 'False' (including quotes) to indicate if an entry point is being used
# [Images_Width] Width of all images
# [Tile_Width] Width of the tiles that make up the images
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
			     InitialForwardHeading=int(forw_headings[idx])).save()

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
        return
    
    # Matches the format of the information
    reg = re.finditer(r"\{(\d+|None),\n(\d+),\n('[\w\s,.'\-]*'),\n(\d+),\n(\d+),\n('[\w\s,.'\-]*'|None),\n('[\w\s,.'\-]*'|None),\n('[\w\s,.!'\"\-]*'|None)\}", file.read())

    vals = []

    for r in reg:
        vals.append(r.groups())

    for v in vals:

        try:
            trail = Trail.objects.get(id = int(v[4]))
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            continue

        PointOfInterest(StartPanoNum=int(v[0]),
                        EndPanoNum=int(v[1]),
                        TrailId=trail,
                        Name=strip(v[2], "'"),
                        PoICategory=int(v[3]),
                        Photo=strip(v[5], "'") if v[5] != 'None' else None,
                        Audio=strip(v[6], "'") if v[6] != 'None' else None,
                        Description=strip(v[7], "'") if v[7] != 'None' else None).save()


# Reads in a file listing changes to links and performs those changes
def fixLinksForTrail(Link_Fix_File):
	try:
		file = open(Link_Fix_File)
	except IOError:
		print "Could not open file. Please make sure it exists."
		return

	data = file.read()
	rem = re.finditer(r"remove (\d+) (\d+) '(Forward|Backwards)'\n", data)
	ins = re.finditer(r"insert (\d+) (\d+) (\d+) (\d+) '(Forward|Backwards)'\n", data)

	removals = []
	insertions = []

	# removal
	# 0 - TrailId
	# 1 - PanoNumber
	# 2 - Link Description

	# insertion
	# 0 - TrailId
	# 1 - PanoNumber of host pano
	# 2 - PanoNumber of destination pano
	# 3 - Angle
	# 4 - Description

	for r in rem:
		removals.append(r.groups())

	for i in ins:
		insertions.append(i.groups())

	for r in removals:
		print "Trail: %s, Pano: %s, Desc: %s" % (r[0], r[1], r[2])
		try:
			trail = Trail.objects.get(id = int(r[0]))
			pano = Panorama.objects.get(TrailId = trail, PanoNumber = int(r[1]))
		except (ObjectDoesNotExist, MultipleObjectsReturned):
			print "Could not match Trail or Panorama specified."
			continue

		try:
			link = Link.objects.get(TrailId = trail, PanoId = pano, Description = r[2])
			link.delete()
		except (ObjectDoesNotExist, MultipleObjectsReturned):
			print "Could not find the defined link."
			continue

	for i in insertions:
		print "Trail: %s, Host: %s, Dest: %s, Angle: %s, Desc: %s" % (i[0], i[1], i[2], i[3], i[4])
		try:
			trail = Trail.objects.get(id = int(i[0]))
			host_pano = Panorama.objects.get(TrailId = trail, PanoNumber = int(i[1]))
			dest_pano = Panorama.objects.get(TrailId = trail, PanoNumber = int(i[2]))
		except (ObjectDoesNotExist, MultipleObjectsReturned):
			print "Could not match Trail or one of the Panoramas specified."
			continue

		link = Link(PanoId=host_pano,
								TrailId=trail,
								Heading=int(i[3]),
								Description=i[4],
								PanoName=dest_pano.Name,
								IsEntryPano=False)

		link.save()

