# TrailView Views

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from trailview.Models import models
from trailview.JSModels import jsmodels
from string import rstrip
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
def Map_ViewTrailById(request, trail_id, pano_id='-1'):
	# This is only called on the first load, so reset original_panos
	original_panos = []

	if pano_id == '-1':
		pano_id = models.Panorama.objects.get(TrailId = int(trail_id), PanoNumber = 0).id

	pano_count = models.Panorama.objects.filter(TrailId = int(trail_id)).count()
	center_pano = models.Panorama.objects.get(TrailId = int(trail_id), id = int(pano_id))

	bottom = center_pano.PanoNumber - surrounding_panos
	bottom = bottom if bottom >= 0 else 0
	top = center_pano.PanoNumber + surrounding_panos + 1
	top = top if top <= pano_count else pano_count

	pano_nums = range(bottom, top)

	trail_name = models.Trail.objects.get(id = int(trail_id)).Name
	panos = models.Panorama.objects.filter(TrailId = int(trail_id), PanoNumber__in = pano_nums)
 	links = models.Link.objects.filter(TrailId = int(trail_id), PanoId__in = map(lambda x: x.id, panos))
 	pois = models.PointOfInterest.objects.filter(TrailId = int(trail_id))

	pano_models = []

	for p in panos:
		link_models = []
		poi_models = []
		for l in links.filter(PanoId = p.id):
			link_models.append(jsmodels.LinkModel(heading=l.Heading,
												  pano=l.PanoName,
												  description=l.Description).__dict__)

		for poi in pois.filter(StartPanoNum__lte = p.PanoNumber, EndPanoNum__gte = p.PanoNumber):
			name = poi.Name.replace('"', '&quot;').replace("'", "&#39")
			desc = (rstrip(poi.Description[:97], " .,'") + "...").replace('"', '&quot;').replace("'", "&#39") if poi.Description else ''
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
	for twp in pois.filter(StartPanoNum = None, EndPanoNum = None):
		name = poi.Name.replace('"', '&quot;').replace("'", "&#39")
		desc = (rstrip(poi.Description[:97], " .,'") + "...").replace('"', '&quot;').replace("'", "&#39") if poi.Description else ''
		twpoi_models.append(jsmodels.PointOfInterestInitModel(Name=name, 
															  Description=desc, 
															  Category=poi.PoICategory).__dict__)

	panos_json = simplejson.dumps(pano_models, use_decimal=True)
	twpoi_json = simplejson.dumps(twpoi_models, use_decimal=True)
	
	pano_count = models.Panorama.objects.filter(TrailId = int(trail_id)).count()

	model = jsmodels.MapDataModel(PanoramasInJSON=panos_json, 
								  initialPanoName=center_pano.Name, 
								  trailName=trail_name, 
								  totalPanos=pano_count, 
								  surroundingPanos=surrounding_panos, 
								  TrailWidePoIsInJSON=twpoi_json)

	original_panos.extend(pano_nums)

	return render_to_response('MapView.html', {'model' : model})

# Retrieves a subset of the remaining panoramas for a given trail
# Only accessible via POST
@require_POST
def Map_RequestMoreData(request):
  trail_name = request.POST.get('trailName', '')
  num = int(request.POST.get('num', '-1'))

  if(trail_name == '' or num == -1):
    return HttpResponse(status=400)

  trail_id = models.Trail.objects.get(Name = trail_name)
  total_panos = models.Panorama.objects.filter(TrailId = trail_id).count()

  nums = range(num, min(panos_to_request + num + 1, total_panos + 1))
  panos = models.Panorama.objects.filter(TrailId = trail_id, PanoNumber__in = nums)
  links = models.Link.objects.filter(TrailId = trail_id, PanoId__in = map(lambda x: x.id, panos))
  pois = models.PointOfInterest.filter(TrailId = trail_id)

  pano_models = []
  for p in panos:
		link_models = []
		poi_models = []
		for l in links.filter(PanoId = p.id):
			link_models.append(jsmodels.LinkModel(heading=l.Heading,
												  pano=l.PanoName,
												  description=l.Description).__dict__)

		for poi in pois.filter(StartPanoNum__lte = p.PanoNumber, EndPanoNum__gte = p.PanoNumber):
			name = poi.Name.replace('"', '&quot;').replace("'", "&#39")
			desc = (rstrip(poi.Description[:97], " .,'") + "...").replace('"', '&quot;').replace("'", "&#39") if poi.Description else ''
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

  model = {
  	'next': ((num + panos_to_request) if ((num + panos_to_request) <= total_panos) else -1),
  	'panos': pano_models
  }

  return HttpResponse(simplejson.dumps(model, use_decimal=True), mimetype='application/json')
