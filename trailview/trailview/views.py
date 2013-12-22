# TrailView Views

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
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
    panos = None
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
    
    if panos == None:
		  panos = models.Panorama.objects.filter(TrailId = int(trail_id), PanoNumber__in = map(lambda x: x.StartPanoNum or -1, pois))

    # create JSModels for markers and return json of them
    markers = []
    count = 0

    for p in panos:
      title = pois.filter(StartPanoNum = p.PanoNumber)[0].Name if (pois != None) else ''

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
	original_panos[:] = []

	if pano_id == '-1':
		try:
			pano_id = models.Panorama.objects.get(TrailId = int(trail_id), PanoNumber = 0).id
		except (ObjectDoesNotExist, MultipleObjectsReturned):
			return HttpResponse(status=400)

	try:
		pano_count = models.Panorama.objects.filter(TrailId = int(trail_id)).count()
		center_pano = models.Panorama.objects.get(TrailId = int(trail_id), id = int(pano_id))
	except (ObjectDoesNotExist, MultipleObjectsReturned):
		return HttpResponse(status=400)

	bottom = center_pano.PanoNumber - surrounding_panos
	bottom = bottom if bottom >= 0 else 0
	top = center_pano.PanoNumber + surrounding_panos + 1
	top = top if top <= pano_count else pano_count

	pano_nums = range(bottom, top)

	try:
		trail_name = models.Trail.objects.get(id = int(trail_id)).Name
		panos = models.Panorama.objects.filter(TrailId = int(trail_id), PanoNumber__in = pano_nums)
	 	links = models.Link.objects.filter(TrailId = int(trail_id), PanoId__in = map(lambda x: x.id, panos))
	 	pois = models.PointOfInterest.objects.filter(TrailId = int(trail_id))
 	except (ObjectDoesNotExist, MultipleObjectsReturned):
 		trail_name = '[Unknown Trail: %s]' % trail_id

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

# Enters a trail indexed by PanoNumber instead of id
def Map_ViewTrailByPanoNum(request, trail_id, pano_num):
	try:
		pano_id = models.Panorama.objects.get(TrailId = int(trail_id), PanoNumber = int(pano_num)).id
	except (ObjectDoesNotExist, MultipleObjectsReturned):
		return HttpResponse(status=400)

	return Map_ViewTrailById(request, trail_id, str(pano_id))
	#return redirect('Map_ViewTrailById', args=(str(trail_id), str(pano_id)), kwargs={}) # **Doesn't work??

# Retrieves a subset of the remaining panoramas for a given trail
# Only accessible via POST
@require_POST
def Map_RequestMoreData(request):
  
  trail_name = request.POST.get('trailName', '')
  num = int(request.POST.get('num', '-1'))

  if(trail_name == '' or num == -1):
    return HttpResponse(status=400)

  try:
  	trail_id = models.Trail.objects.get(Name = trail_name)
  except (ObjectDoesNotExist, MultipleObjectsReturned):
  	return HttpResponse(status=400)

  total_panos = models.Panorama.objects.filter(TrailId = trail_id).count()

  nums = range(num, min(panos_to_request + num, total_panos + 1))
  nums = filter(lambda x: not x in original_panos, nums)
  panos = models.Panorama.objects.filter(TrailId = trail_id, PanoNumber__in = nums)
  links = models.Link.objects.filter(TrailId = trail_id, PanoId__in = map(lambda x: x.id, panos))
  pois = models.PointOfInterest.objects.filter(TrailId = trail_id)

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

# Function retrieves information about a point of interest and returns it
# for display in a dialog box
@require_POST
def Map_GetPointOfInterest(request):
	poi_name = request.POST.get('poi_name', '')
	pano_num = int(request.POST.get('pano_num', '-1'))

	try:
		poi = models.PointOfInterest.objects.get(Name = poi_name, StartPanoNum__lte = pano_num, EndPanoNum__gte = pano_num)
	except (ObjectDoesNotExist, MultipleObjectsReturned):
		return HttpResponse(status=400)

	p = jsmodels.PointOfInterestModel(Name=poi.Name,
	                                  Photo=poi.Photo,
	                                  Audio=poi.Audio,
	                                  Description=poi.Description,
	                                  Category=poi.PoICategory).__dict__

	return HttpResponse(simplejson.dumps(p, use_decimal=True), mimetype='application/json')
