import json
import pathlib

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType


from apis_instance_nsvis.models import Institution, Person, Place, AddressData, MongoDbModel


class Command(BaseCommand):
    help = "Import data from MongoDB dump"

    def add_arguments(self, parser):
        parser.add_argument('--dumpdir', type=pathlib.Path)

    def handle(self, *args, **options):
        dumpdir = options["dumpdir"]
        for file in dumpdir.glob("*.json"):
            match file.stem:
                case "agencies":
                    data = json.loads(file.read_text())
                    for agency in data:
                        inst, created = Institution.objects.get_or_create(label=agency["name"])
                        content_type = ContentType.objects.get_for_model(inst)
                        mdbdata, created = MongoDbModel.objects.get_or_create(data=data, filename=file.name, content_type=content_type, object_id=inst.id)
                case _:
                    pass
