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

    def _sortissues(self, issue):
        if "Maerz " in issue:
            year = issue.replace("Maerz ", "")
            issue = f"01.03.{year}"
        if "November " in issue:
            year = issue.replace("November ", "")
            issue = f"01.11.{year}"
        try:
            return datetime.strptime(issue, "%d.%m.%Y")
        except ValueError:
            logger.error("Could not parse %s", issue)
            return datetime.now()

    def __init__(self):
        magazines_sorted_file = getattr(settings, "MAGAZINES_SORTED", None)
        if magazines_sorted_file:
            self.magazines_sorted = json.loads(magazines_sorted_file.read_text())
        for magazine, years in self.magazines_sorted.items():
            self.magazines_sorted[magazine] = {
                k: v for k, v in sorted(self.magazines_sorted[magazine].items())
            }
            for year in years:
                self.magazines_sorted[magazine][year] = {
                    k: v
                    for k, v in sorted(
                        self.magazines_sorted[magazine][year].items(),
                        key=lambda x: self._sortissues(x[0]),
                    )
                }

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

    def get_issues_per_magazine(self):
        data = {}
        for magazine, years in self.magazines_sorted.items():
            data[magazine] = {}
            for year, issues in years.items():
                data[magazine] |= issues
        return data


class MyImgProxy:
    def __init__(self, *args, **kwargs):
        self.key = os.getenv("IMGPROXY_KEY")
        self.salt = os.getenv("IMGPROXY_SALT")
        self.proxy_host = "https://imgproxy.acdh.oeaw.ac.at"

    def img_url(self, path):
        path = f"s3://for-imgproxy/{path}"
        return ImgProxy(path, proxy_host=self.proxy_host, key=self.key, salt=self.salt)

    def calc(self, path):
        return self.img_url(path)()

    def crop(self, path, width, height, x=0, y=0):
        gravity = f"nowe:{x}:{y}"
        crop = f"crop:{width}:{height}:{gravity}"
        return self.img_url(path)(crop, width=800, height=800, resizing_type="fit")

    def resize(self, path, width=150, height=200):
        return self.img_url(path)(width=width, height=height, resizing_type="fit")


re_abseit = r"^(vor|ab|seit|um) (?P<year>\d{1,4})"
re_nach = r"^nach (?P<year>\d{1,4})"


def customdateparser(date_string: str) -> tuple[datetime, datetime, datetime]:
    date_string = date_string.lower()
    if match := re.match(re_abseit, date_string):
        date_string = f"1.1.{match['year']}"
    if match := re.match(re_nach, date_string):
        date_string = f"31.12.{match['year']}"
    return defaultdateparser(date_string)
