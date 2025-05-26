import json
import logging
import os
import pathlib
import boto3
from imgproxy import ImgProxy
from botocore.exceptions import ClientError
from botocore.config import Config
from datetime import datetime
import re
from django_interval.utils import defaultdateparser

logger = logging.getLogger(__name__)


class S3:
    cachefile = pathlib.Path("/tmp/s3_cache.json")

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, *args, **kwargs):
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        endpoint_url = os.getenv("AWS_ENDPOINT_URL")
        self.s3_bucket = "for-imgproxy"
        if aws_access_key_id and aws_secret_access_key and endpoint_url:
            self.session = boto3.session.Session()
            config = Config(
                    tcp_keepalive=True,
                    request_checksum_calculation="when_required",
                    response_checksum_validation="when_required")

            self.client = self.session.client("s3",
                                       endpoint_url=endpoint_url,
                                       aws_access_key_id=aws_access_key_id,
                                       aws_secret_access_key=aws_secret_access_key,
                                       config=config)

    def upload_file(self, path, target=None):
        target = target or pathlib.Path(path).name
        try:
            response = self.client.upload_file(path, self.s3_bucket, target)
            self.filecache_append(target)
        except ClientError as e:
            logging.error("Could not upload file to s3 bucket %s: %s", s3_bucket, e)

    def file_exists(self, path):
        return path in self.filecache

    @property
    def filecache(self):
        if not self.cachefile.exists():
            data = []
            s3_paginator = self.client.get_paginator('list_objects_v2')
            s3_page_iterator = s3_paginator.paginate(Bucket=self.s3_bucket, Prefix="23503")
            for page in s3_page_iterator:
                data.extend([obj["Key"] for obj in page.get("Contents", [])])
            self.cachefile.write_text(json.dumps(data))
        return json.loads(self.cachefile.read_text())

    def filecache_append(self, item):
        data = self.filecache
        data.append(item)
        self.cachefile.write_text(json.dumps(data))


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
