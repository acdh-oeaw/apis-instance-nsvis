import json
import logging
import os
from imgproxy import ImgProxy
from datetime import datetime
import re
from django_interval.utils import defaultdateparser
from django.conf import settings

logger = logging.getLogger(__name__)


class Magazines:
    magazines_sorted: dict = {}

    def __init__(self):
        magazines_sorted_file = getattr(settings, "MAGAZINES_SORTED", None)
        if magazines_sorted_file:
            self.magazines_sorted = json.loads(magazines_sorted_file.read_text())

    def get_path_for_url(self, url):
        for magazine, years in self.magazines_sorted.items():
            for year, issues in years.items():
                for issue, pages in issues.items():
                    for page in pages:
                        if page["labelledurl"] == url:
                            return page["iiifpath"]
        return None

    def get_imgproxy_path_for_url(self, url):
        path = self.get_path_for_url(url)
        return f"23503/new/{path}.jpg"


class MyImgProxy:
    def __init__(self, *args, **kwargs):
        self.key = os.getenv("IMGPROXY_KEY")
        self.salt = os.getenv("IMGPROXY_SALT")
        self.proxy_host = "https://imgproxy.acdh.oeaw.ac.at"

    def calc(self, path):
        img_url = ImgProxy(f"s3://for-imgproxy/{path}",
                        proxy_host=self.proxy_host,
                        key=self.key,
                        salt=self.salt)
        return img_url()

    def crop(self, path, width, height, x=0, y=0):
        gravity = f"nowe:{x}:{y}"
        crop = f"crop:{width}:{height}:{gravity}"
        img_url = ImgProxy(f"s3://for-imgproxy/{path}",
                        proxy_host=self.proxy_host,
                        key=self.key,
                        salt=self.salt)
        return img_url(crop, width=800, height=800, resizing_type="fit")



re_abseit = r"^(vor|ab|seit|um) (?P<year>\d{1,4})"
re_nach = r"^nach (?P<year>\d{1,4})"


def customdateparser(date_string: str) -> tuple[datetime, datetime, datetime]:
    date_string = date_string.lower()
    if match := re.match(re_abseit, date_string):
        date_string = f"1.1.{match['year']}"
    if match := re.match(re_nach, date_string):
        date_string = f"31.12.{match['year']}"
    return defaultdateparser(date_string)
