from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Trails
class Trail(models.Model):
	TrailId = models.IntegerField(primary_key=True)
	Name = models.CharField(max_length=100)
	
	def __unicode__(self):
		return self.Nam
		
# Panoramas
class Panorama(models.Model):
	PanoId = models.IntegerField(primary_key=True)
	TrailId = models.ForeignKey(Trail)
	Name = models.CharField(max_length=100)
	Description = models.CharField(max_length=1000)
	LocationLat = models.DecimalField(max_digits=30, decimal_places=25)
	LocationLng = models.DecimalField(max_digits=30, decimal_places=25)
	TileWidth = models.IntegerField()
	WorldWidth = models.IntegerField()
	ForwardHeading = models.IntegerField()
	InitialForwardHeading = models.IntegerField()
	
	def __unicode__(self):
		return "%d(%d)" % (TrailId, PanoId)
		
# Links
class Link(models.Model):
	LinkId = models.IntegerField(primary_key=True)
	PanoId = models.ForeignKey(Panorama)
	TrailId = models.ForeignKey(Trail)
	Heading = models.IntegerField()
	Description = models.CharField(max_length=1000)
	PanoName = models.CharField(max_length=100)
	IsEntryPano = models.BooleanField()
	
	def __unicode__(self):
		return "%d(%d):%s" % (self.PanoId, self.LinkId, self.PanoName)
		
# Points of Interest
class PointOfInterest(models.Model):
	POIId = models.IntegerField(primary_key=True)
	StartPanoNum = models.IntegerField(null=True)
	EndPanoNum = models.IntegerField(null=True)
	TrailId = models.ForeignKey(Trail)
	Name = models.CharField(max_length=100)
	PoICategory = models.IntegerField()
	Photo = models.CharField(max_length=100)
	Audio = models.CharField(max_length=100)
	Description = models.CharField(max_length=1000)
	
	def __unicode__(self):
		return "%s%d" % (self.Name, self.PoIId)
		
class PoICategory:
	Atmospheric = 0
	Fauna = 1
	Flora = 2
	Landmark = 3
