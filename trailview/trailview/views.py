# TrailView Views

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from trailview.Models import models
from trailview.JSModels import jsmodels
import simplejson

import pdb

original_panos = []
surrounding_panos = 7
panos_to_request = 50

# Request for Home Page
def Home_Home(request):
    return render_to_response('Home.html', {})

# Request for page listing all Trails
def Trails_Trails(request):
	filter_options = [jsmodels.TrailPointSelectionFilter(value="All", text="All Panoramas"),
	                  jsmodels.TrailPointSelectionFilter(value="PoIs", text="All Points of Interest"),
	                  jsmodels.TrailPointSelectionFilter(value="Atmo", text="Atmospherics"),
	                  jsmodels.TrailPointSelectionFilter(value="Fau", text="Fauna"),
	                  jsmodels.TrailPointSelectionFilter(value="Flo", text="Flora"),
	                  jsmodels.TrailPointSelectionFilter(value="Lan", text="Landmarks")]
	trails = models.Trail.objects.all()
	return render_to_response('Trails.html', {'trails': trails, 'filter_options': filter_options})

def Trails_GetPossibleEntryPoints(request):

    trail_id = request.POST.get('trailId', None)
    filter = request.POST.get('filter', None)
    
    if trail_id == None or filter == None:
      return HttpResponse(status=400)
    
    pois = None
    if(filter == 'PoIs'):
        pois = models.PointOfInterest.objects.filter(TrailId = int(trail_id))
    elif(filter == 'Atmo'):
        pois = models.PointOfInterest.objects.filter(TrailId = int(trail_id), PoICategory = models.PoICategory.Atmospheric)
    elif(filter == 'Fau'):
        pois = models.PointOfInterest.objects.filter(TrailId = int(trail_id), PoICategory = models.PoICategory.Fauna)
    elif(filter == 'Flo'):
        pois = models.PointOfInterest.objects.filter(TrailId = int(trail_id), PoICategory = models.PoICategory.Flora)
    elif(filter == 'Lan'):
        pois = models.PointOfInterest.objects.filter(TrailId = int(trail_id), PoICategory = models.PoICategory.Landmark)
    else:
        panos = models.Panorama.objects.filter(TrailId = int(trail_id))
    
    if not 'panos' in locals():
        panos = models.Panorama.objects.filter(TrailId = int(trail_id), PanoNumber__in = map(lambda x: x.StartPanoNum or -1, pois))

    # create JSModels for markers and return json of them
    markers = []
    count = 0

    for p in panos:
        try:
            title = pois.filter(StartPanoNum = p.PanoNumber)[0].Name if (pois != None) else ''
        except ObjectDoesNotExist:
            title = ''

        markers.append(jsmodels.MarkerModel(LocationLat=p.LocationLat,
                                                 LocationLng=p.LocationLng,
                                                 PanoId=p.id,
                                                 TrailId=p.TrailId.id,
                                                 orderOfMarkers=count,
                                                 Title=title).__dict__)
        count += 1
    
    return HttpResponse(simplejson.dumps(markers, use_decimal=True), mimetype='application/json')

# Request for Map by trail_id
def Map_ViewTrailById(request, trail_id):
	trail = models.Trail.objects.get(id = int(trail_id))
	panos = models.Panorama.objects.filter(TrailId = int(trail_id), PanoNumber__lte = surrounding_panos)
	pano_models = []
	for p in panos:
		link_models = []
		poi_models = []
		for l in models.Link.objects.filter(TrailId = int(trail_id), PanoId = p.id):
			link_models.append(jsmodels.LinkModel(heading=l.Heading,
												  pano=l.PanoName,
												  description=l.Description).__dict__)

		for poi in models.PointOfInterest.objects.filter(TrailId = int(trail_id), StartPanoNum__gte = p.PanoNumber, EndPanoNum__lte = p.PanoNumber):
			name = poi.Name.replace('"', '&quot;').replace("'", "&#39")
			desc = poi.Description[:97].rstrip(" ", ".", ",", "'").extend("...").replace('"', '&quot;').replace("'", "&#39") if poi.Description else ''
			poi_models.append(jsmodels.PointOfInterestInitModel(Name=name,
																Description=desc, 
																Category=poi.PoICategory).__dict__)

		pano_models.append(jsmodels.PanoramaModel(Name=p.Name, 
												  Description=p.Description,
												  PanoNumber=p.PanoNumber, 
												  LocationLat=p.LocationLat, 
												  LocationLng=p.LocationLng,
												  TileWidth=p.TileWidth, 
												  ImageWidth=p.WorldWidth, 
												  ForwardHeading=p.ForwardHeading, 
												  InitialHeading=p.InitialForwardHeading, 
												  Links=link_models, 
												  PointsOfInterest=poi_models).__dict__)

	twpoi_models = []
	for twp in models.PointOfInterest.objects.filter(TrailId = int(trail_id), StartPanoNum = None, EndPanoNum = None):
		name = poi.Name.replace('"', '&quot;').replace("'", "&#39")
		desc = poi.Description[:97].rstrip(" ", ".", ",", "'").extend("...").replace('"', '&quot;').replace("'", "&#39") if poi.Description else ''
		twpoi_models.append(jsmodels.PointOfInterestInitModel(Name=name, 
															  Description=desc, 
															  Category=poi.PoICategory).__dict__)

	panos_json = simplejson.dumps(pano_models, use_decimal=True)
	twpoi_json = simplejson.dumps(twpoi_models, use_decimal=True)
	
	pano_count = models.Panorama.objects.count()

	model = jsmodels.MapDataModel(PanoramasInJSON=panos_json, 
								  initialPanoName="", 
								  trailName=trail.Name, 
								  totalPanos=pano_count, 
								  surroundingPanos=surrounding_panos, 
								  TrailWidePoIsInJSON=twpoi_json)

	original_panos.extend(range(0, surrounding_panos + 1))

	return render_to_response('MapView.html', {'model' : model})

# Request for map by trail_id, loading at panorama with pano_id
def Map_ViewTrailStartingAtPano(request, trail_id, pano_id):
	return "asdf"
