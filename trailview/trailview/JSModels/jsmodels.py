# Models that represent everything the object needs to be handled on the client
# side. This is generally much less (occasionally some additional fields come in)
# than what is needed to manage them in the database

class LinkModel(object):
	def __init__(self, heading, pano, description):
		self.heading = heading
		self.pano = pano
		self.description = description

class MapDataModel(object):
	def __init__(self, PanoramasInJSON, initialPanoName, trailName, totalPanos, surroundingPanos, TrailWidePoIsInJSON):
		self.PanoramasInJSON = PanoramasInJSON
		self.initialPanoName = initialPanoName
		self.trailName = trailName
		self.totalPanos = totalPanos
		self.surroundingPanos = surroundingPanos
		self.TrailWidePoIsInJSON = TrailWidePoIsInJSON

class MarkerModel(object):
	def __init__(self, LocationLat, LocationLng, TrailId, PanoId, orderOfMarkers, Title):
		self.LocationLat = LocationLat
		self.LocationLng = LocationLng
		self.TrailId = TrailId
		self.PanoId = PanoId
		self.orderOfMarkers = orderOfMarkers
		self.Title = Title

class PanoramaModel(object):
	def __init__(self, Name, Description, PanoNumber, LocationLat, LocationLng, TileWidth, ImageWidth, ForwardHeading, InitialHeading, Links, PointsOfInterest):
		self.Name = Name
		self.Description = Description
		self.PanoNumber = PanoNumber
		self.LocationLat = LocationLat
		self.LocationLng = LocationLng
		self.TileWidth = TileWidth
		self.ImageWidth = ImageWidth
		self.ForwardHeading = ForwardHeading
		self.InitialHeading = InitialHeading
		self.Links = Links
		self.PointsOfInterest = PointsOfInterest

class PointOfInterestInitModel(object):
	def __init__(self, Name, Description, Category):
		self.Name = Name
		self.Description = Description
		self.Category = Category

class PointOfInterestModel(object):
	def __init__(self, Name, Photo, Audio, Description, Category):
		self.Name = Name
		self.Photo = Photo
		self.Audio = Audio
		self.Description = Description
		self.Category = Category

class PointsOfInterestListModel(object):
	def __init__(self, Trails, atmo, fau, flo, lan):
		self.Trails = Trails
		self.atmo = atmo
		self.fau = fau
		self.flo = flo
		self.lan = lan

class PointsOfInterestWithTrailsModel(object):
	def __init__(self, PoIs, Trails):
		self.PoIs = PoIs
		self.Trails = Trails

class TrailsModel(object):
	def __init__(self, Trials, dropDownListValues):
		self.Trails = Trails
		self.dropDownListValues = dropDownListValues

class TrailPointSelectionFilter(object):
	def __init__(self, value, text):
		self.value = value
		self.text = text
