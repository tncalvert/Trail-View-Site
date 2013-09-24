# Various inclusions for Trail View

from django import template
from trailview.Models.models import Trail
register = template.Library()

@register.inclusion_tag('_header_banner.html')
def render_header_banner():
	return {} # empty dictionary, there isn't anything needed here

@register.inclusion_tag('_menu_bar.html')
def render_menu_bar():
	trails = Trail.objects.all()
	return { 'trials': trails }
