import json
from django import template
from django.conf import settings
from pathlib import Path
from apis_instance_nsvis.utils import MyImgProxy

register = template.Library()


@register.filter
def pretty_json(value):
    return json.dumps(value, indent=2)


@register.filter
def magazine_short(value):
    return value.split("-")[0].strip()


@register.filter
def parse_iiif_link(value):
    base = value.split(".jp2/")[0]
    return base + ".jp2"


@register.filter
def iiif_preview(value):
    return parse_iiif_link(value) + "/full/150,/0/default.jpg"


@register.simple_tag
def magazines():
    magazine_file = getattr(settings, "MAGAZINE_FILE", None)
    if magazine_file is not None:
        return json.loads(Path(magazine_file).read_text())
    return {}


@register.filter
def get_imgproxypath_for_labelled_url(url):
    for magazine, issues in magazines().items():
        for issue, pages in issues.items():
            for page in pages:
                if page["labelledurl"] == url:
                    return page["iiifpath"]
    return None


@register.filter
def get_real_url_for_labelled_url(url):
    imgproxy = MyImgProxy()
    path = get_imgproxypath_for_labelled_url(url)
    if path:
        return imgproxy.calc(f"23503/new/{path}.jpg")
    return None


@register.filter
def get_thumbnail_for_labelled_url(url):
    imgproxy = MyImgProxy()
    path = get_imgproxypath_for_labelled_url(url)
    if path:
        return imgproxy.resize(f"23503/new/{path}.jpg")
    return None
