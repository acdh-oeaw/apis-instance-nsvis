import json
from django import template
from apis_instance_nsvis.utils import MyImgProxy
from apis_instance_nsvis.models import MagazinePage

register = template.Library()


@register.filter
def pretty_json(value):
    return json.dumps(value, indent=2)


@register.filter
def get_imgproxy_url_for_labelled_url(url):
    magazinepage = MagazinePage.objects.get(origurl=url)
    imgproxy = MyImgProxy()
    return imgproxy.calc(f"23503/new/{magazinepage.path}.jpg")


@register.filter
def get_imgproxy_thumbnail_for_labelled_url(url):
    magazinepage = MagazinePage.objects.get(origurl=url)
    imgproxy = MyImgProxy()
    return imgproxy.resize(f"23503/new/{magazinepage.path}.jpg")
