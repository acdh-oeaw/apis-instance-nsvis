import functools
import logging
import os
import pathlib
import boto3
from imgproxy import ImgProxy
from botocore.exceptions import ClientError
from botocore.config import Config

logger = logging.getLogger(__name__)


class S3:
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
        except ClientError as e:
            logging.error("Could not upload file to s3 bucket %s: %s", s3_bucket, e)

    def file_exists(self, path):
        try:
            self.client.head_object(Bucket=self.s3_bucket, Key=path)
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                raise
        else:
            return True


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
