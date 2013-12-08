# TrailView Views

from django.shortcuts import render_to_response
from django.core import serializers
from trailview.Models import models
from trailview.JSModels import jsmodels

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

# Request for Map by trail_id
def Map_ViewTrailById(request, trail_id):
	trail = models.Trail.objects.get(TrailId = int(trail_id))
	panos = models.Panorama.objects.filter(TrailId = int(trail_id), PanoNumber__lte = surrounding_panos)
	pano_models = []
	for p in panos:
		link_models = []
		poi_models = []
		for l in models.Link.objects.filter(TrailId = int(trail_id), PanoId = p.PanoId):
			link_models.append(jsmodels.LinkModel(heading=l.Heading,
												  pano=l.PanoName,
												  description=l.Description))

		for poi in models.PointOfInterest.objects.filter(TrailId = int(trail_id), PanoId = p.PanoId):
			name = poi.Name.replace('"', '&quot;').replace("'", "&#39")
			desc = poi.Description[:97].rstrip(" ", ".", ",", "'").extend("...").replace('"', '&quot;').replace("'", "&#39")
			poi_models.append(jsmodels.PointOfInterestInitModel(Name=name,
																Description=desc, 
																Category=poi.Category))

		pano_models.append(jsmodels.PanoramaModel(Name=p.Name, 
												  Description=p.Description,
												  PanoNumber=p.PanoNumber, 
												  LocationLat=p.LocationLat, 
												  LocationLng=p.LocationLng,
												  TileWidth=p.TileWidth, 
												  ImageWidth=p.ImageWidth, 
												  ForwardHeading=p.ForwardHeading, 
												  InitialHeading=p.InitialHeading, 
												  Links=link_models, 
												  PointsOfInterest=poi_models))

	twpoi_models = []
	for twp in models.PointOfInterest.objects.filter(TrailId = int(trail_id), StartPanoNum = None, EndPanoNum = None):
		name = poi.Name.replace('"', '&quot;').replace("'", "&#39")
		desc = poi.Description[:97].rstrip(" ", ".", ",", "'").extend("...").replace('"', '&quot;').replace("'", "&#39")
		twpoi_models.append(jsmodels.PointOfInterestInitModel(Name=name, 
															  Description=desc, 
															  Category=poi.Category))

	panos_json = serializers.serialize('json', pano_models)
	twpoi_json = serializers.serialize('json', twpoi_models)

	model = jsmodels.MapDataModel(PanoramasInJSON=panos_json, 
								  initialPanoName="", 
								  trailName=trail.Name, 
								  totalPanos=models.Panorama.count, 
								  surroundingPanos=surrounding_panos, 
								  TrailWidePoIsInJSON=twpoi_json)

	original_panos.extend(range(0, surrounding_panos + 1))

	return render_to_response('MapView.html', {'model' : model})

# Request for map by trail_id, loading at panorama with pano_id
def Map_ViewTrailStartingAtPano(request, trail_id, pano_id):
	return "asdf"
