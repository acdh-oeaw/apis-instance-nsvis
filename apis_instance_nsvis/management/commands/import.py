import json
import pathlib

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


from apis_instance_nsvis.models import (
        MongoDbModel,
        Person,
        Place,
        Institution,
        IsMemberOf,
        IsLearningAt,
        IsInventoriedIn,
        AddressData,
        AddressInPlace,
        LivesIn)


def parse_address(address_data):
    address = address_data.get("adress")
    postal = address_data.get("postal")
    if address and postal:
        addd, created = AddressData.objects.get_or_create(address=address, postal=postal)
        addd_ct = ContentType.objects.get_for_model(addd)
        city = address_data.get("city")
        place, created = Place.objects.get_or_create(label=city)
        place_ct = ContentType.objects.get_for_model(place)
        aip, created = AddressInPlace.objects.get_or_create(subj_content_type=addd_ct, subj_object_id=addd.id, obj_content_type=place_ct, obj_object_id=place.id)
        return addd
    return None


def parse_photographer(mdbm):
    photographer = mdbm.data
    for membership in photographer.get("membership", {}).get("membershiplist", []):
        oid = membership["membership"]
        membership = MongoDbModel.objects.get(filename="memberships.json", data___id=oid)
        rel, created = IsMemberOf.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=membership.content_type, obj_object_id=membership.object_id)
    for party in photographer.get("politicalactivity", {}).get("party", []):
        party = MongoDbModel.objects.get(filename="parties.json", data___id=party)
        rel, created = IsMemberOf.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=party.content_type, obj_object_id=party.object_id)
    for education in photographer.get("education", {}).get("educationlist", []):
        oid = education["institution"]
        institution = MongoDbModel.objects.get(filename="institutions.json", data___id=oid)
        rel, created = IsLearningAt.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=institution.content_type, obj_object_id=institution.object_id)
    for inventory in photographer.get("inventorylist", []):
        oid = inventory["inventory"]
        inventory = MongoDbModel.objects.get(filename="inventories.json", data___id=oid)
        rel, created = IsInventoriedIn.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=inventory.content_type, obj_object_id=inventory.object_id)
    for address in photographer.get("basicdata", {}).get("adresses", []):
        addd = parse_address(address)
        if addd:
            addd_ct = ContentType.objects.get_for_model(addd)
            rel, created = LivesIn.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=addd_ct, obj_object_id=addd.id)


class Command(BaseCommand):
    help = "Import data from MongoDB Export"

    def add_arguments(self, parser):
        parser.add_argument("file", type=pathlib.Path)

    def handle(self, *args, **options):
        for json_file in options["file"].glob("*.json"):
            data = json.loads(json_file.read_text())
            for item in data:
                mdbm, created = MongoDbModel.objects.get_or_create(data=item, filename=json_file.name)
                if mdbm.content_object is None:
                    if json_file.stem in ["photographers", "agencypeople"]:
                        mdbm.content_object = Person.objects.create()
                        mdbm.save()
                    if json_file.stem in ["agencies", "inventories", "memberships", "parties", "institutions"]:
                        mdbm.content_object = Institution.objects.create()
                        mdbm.save()
                match json_file.stem:
                    case "photographers":
                        basicdata = mdbm.data["basicdata"]
                        mdbm.content_object.surname=basicdata["surname"]
                        mdbm.content_object.forename=basicdata["name"]
                        mdbm.content_object.save()
                    case "agencypeople":
                        mdbm.content_object.surname=mdbm.data["surname"]
                        mdbm.content_object.forename=mdbm.data["name"]
                        mdbm.content_object.save()
                    case "agencies":
                        mdbm.content_object.label=mdbm.data["name"]
                        mdbm.content_object.save()
                    case "inventories":
                        mdbm.content_object.label=mdbm.data["fullname"]
                        mdbm.content_object.save()
                    case "memberships":
                        mdbm.content_object.label=mdbm.data["fullname"]
                        mdbm.content_object.save()
                    case "parties":
                        mdbm.content_object.label=mdbm.data["fullname"]
                        mdbm.content_object.save()
                    case "institutions":
                        mdbm.content_object.label=mdbm.data["fullname"]
                        mdbm.content_object.save()
        for mdbm in MongoDbModel.objects.filter(filename="photographers.json"):
            parse_photographer(mdbm)
