from django.db import models

# Trails
class Trail(models.Model):
	# id is default pk
	Name = models.CharField(max_length=100)
	
	def __unicode__(self):
		return self.Name
		
# Panoramas
class Panorama(models.Model):
	# id is default pk
	TrailId = models.ForeignKey(Trail)
	Name = models.CharField(max_length=100)
	Description = models.CharField(max_length=1000)
	PanoNumber = models.IntegerField()
	LocationLat = models.DecimalField(max_digits=30, decimal_places=25)
	LocationLng = models.DecimalField(max_digits=30, decimal_places=25)
	TileWidth = models.IntegerField()
	WorldWidth = models.IntegerField()
	ForwardHeading = models.IntegerField()
	InitialForwardHeading = models.IntegerField()
	
	def __unicode__(self):
		return "%s(%d)" % (self.TrailId, self.id)
		
# Links
class Link(models.Model):
	# id is default pk
	PanoId = models.ForeignKey(Panorama)
	TrailId = models.ForeignKey(Trail)
	Heading = models.IntegerField()
	Description = models.CharField(max_length=1000)
	PanoName = models.CharField(max_length=100)
	IsEntryPano = models.BooleanField()
	
	def __unicode__(self):
		return "%s(%d):%s" % (self.PanoId, self.id, self.PanoName)
		
# Points of Interest
class PointOfInterest(models.Model):
	# id is default pk
	StartPanoNum = models.IntegerField(null=True)
	EndPanoNum = models.IntegerField(null=True)
	TrailId = models.ForeignKey(Trail)
	Name = models.CharField(max_length=100)
	PoICategory = models.IntegerField()
	Photo = models.CharField(max_length=100, null=True)
	Audio = models.CharField(max_length=100, null=True)
	Description = models.CharField(max_length=1000, null=True)
	
	def __unicode__(self):
		return "%s%s" % (self.Name, self.id)
		
class PoICategory:
	Atmospheric = 0
	Fauna = 1
	Flora = 2
	Landmark = 3
