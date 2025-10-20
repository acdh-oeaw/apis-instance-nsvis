import json
from django import template
from apis_instance_nsvis.utils import MyImgProxy, Magazines

register = template.Library()


@register.filter
def pretty_json(value):
    return json.dumps(value, indent=2)


@register.filter
def get_imgproxy_url_for_labelled_url(url):
    magazines = Magazines()
    path = magazines.get_path_for_url(url)
    imgproxy = MyImgProxy()
    if path:
        return imgproxy.calc(f"23503/new/{path}.jpg")
    return None


@register.filter
def get_imgproxy_thumbnail_for_labelled_url(url):
    magazines = Magazines()
    path = magazines.get_path_for_url(url)
    imgproxy = MyImgProxy()
    if path:
        return imgproxy.resize(f"23503/new/{path}.jpg")
    return None
