import json
import pathlib

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from apis_core.collections.models import SkosCollection


from apis_instance_nsvis.models import *


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


def parse_num(num: int):
    match num:
        case 0:
            return Person.Choices.UNK
        case 1:
            return Person.Choices.NO
        case 2:
            return Person.Choices.YES


def parse_photographer(mdbm):
    photographer = mdbm.data
    photographer_collection, _ = SkosCollection.objects.get_or_create(name="Photographers")
    photographer_collection.add(mdbm.content_object)
    basicdata = photographer.get("basicdata", {})
    mdbm.content_object.comment = basicdata.get("comments", "")
    mdbm.content_object.date_of_birth = basicdata["birthdatestr"]
    mdbm.content_object.date_of_death = basicdata["deathdatestr"]
    mdbm.content_object.membership_comment = photographer.get("membership", {}).get("comments", "")
    mdbm.content_object.exile_comment = photographer.get("politicalactivity", {}).get("exilecomment", "")
    mdbm.content_object.party_comment = photographer.get("politicalactivity", {}).get("partycomment", "")
    mdbm.content_object.profession_comment = photographer.get("profession", {}).get("comments", "")
    research = photographer.get("research", {})
    mdbm.content_object.research_sources = research.get("selection", [])
    if other_research := research.get("selectioncommentother", False):
        mdbm.content_object.research_sources.extend(other_research.split(";"))
    mdbm.content_object.other_sources = photographer.get("othersourceslist", [])
    mdbm.content_object.literature = photographer.get("literaturelist", [])
    mdbm.content_object.work_ban = parse_num(photographer.get("politicalactivity", {}).get("ban", 0))
    mdbm.content_object.work_ns = parse_num(photographer.get("politicalactivity", {}).get("worked", 0))
    mdbm.content_object.propaganda_membership = parse_num(photographer.get("politicalactivity", {}).get("propaganda", 0))

    mdbm.content_object.inheritance = []
    for inheritance in photographer["inheritancelist"]:
        mdbm.content_object.inheritance.append({"contact": inheritance["contact"], "extent": inheritance["extent"], "comment": inheritance["inheritance"]})

    for field in photographer["additonalFields"]:
        # citizenship
        if field["field"] == {'$oid': "5768fcf94b760a6d0500023c"}:
            mdbm.content_object.citizenship = field["value"]

    for area in photographer["specialareas"]["specialareaslist"]:
        mo_special_area = MongoDbModel.objects.get(filename="specialareas.json", data___id=area)
        mdbm.content_object.special_areas.add(mo_special_area.content_object)

    mdbm.content_object.save()

    if birthplace := basicdata.get("birthplace", False):
        birth_place, created = Place.objects.get_or_create(label=birthplace["name"])
        place_ct = ContentType.objects.get_for_model(birth_place)
        rel, created = BornIn.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=place_ct, obj_object_id=birth_place.id)

    if deathplace := basicdata.get("deathplace", False):
        death_place, create = Place.objects.get_or_create(label=deathplace["name"])
        place_ct = ContentType.objects.get_for_model(death_place)
        rel, created = DiedIn.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=place_ct, obj_object_id=death_place.id)

    for membership in photographer.get("membership", {}).get("membershiplist", []):
        oid = membership["membership"]
        mo_membership = MongoDbModel.objects.get(filename="memberships.json", data___id=oid)
        rel, created = IsMemberOf.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=mo_membership.content_type, obj_object_id=mo_membership.object_id)
        rel.from_date = membership["fromdatestr"]
        rel.to_date = membership["todatestr"]
        rel.save()

    for party in photographer.get("politicalactivity", {}).get("party", []):
        party = MongoDbModel.objects.get(filename="parties.json", data___id=party)
        rel, created = IsMemberOf.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=party.content_type, obj_object_id=party.object_id)

    for education in photographer.get("education", {}).get("educationlist", []):
        oid = education["institution"]

        institution = MongoDbModel.objects.get(filename="institutions.json", data___id=oid)
        rel, created = IsLearningAt.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=institution.content_type, obj_object_id=institution.object_id)
        rel.from_date = education["fromdatestr"]
        rel.to_date = education["todatestr"]
        rel.details = education.get("educationtype", "")
        rel.save()

    for profession in photographer.get("profession", {}).get("professionlist", []):
        oid = profession["employer"]

        mo_profession = MongoDbModel.objects.get(filename="employers.json", data___id=oid)
        rel, created = WorksAs.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=mo_profession.content_type, obj_object_id=mo_profession.object_id)
        rel.from_date = profession["fromdatestr"]
        rel.to_date = profession["todatestr"]
        rel.details = profession.get("profession", "")
        rel.save()

    for inventory in photographer.get("inventorylist", []):
        oid = inventory["inventory"]
        mo_inventory = MongoDbModel.objects.get(filename="inventories.json", data___id=oid)
        rel, created = IsInventoriedIn.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=mo_inventory.content_type, obj_object_id=mo_inventory.object_id)
        rel.contact = inventory.get("contact", "")
        rel.extent = inventory.get("extent", "")
        rel.save()

    for address in photographer.get("basicdata", {}).get("adresses", []):
        addd = parse_address(address)
        if addd:
            addd_ct = ContentType.objects.get_for_model(addd)
            if address["living"]:
                rel, created = LivesIn.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=addd_ct, obj_object_id=addd.id)
                rel.from_date = address["fromdatestr"]
                rel.to_date = address["todatestr"]
                rel.save()
            if address["atelier"]:
                rel, created = HasStudioIn.objects.get_or_create(subj_content_type=mdbm.content_type, subj_object_id=mdbm.object_id, obj_content_type=addd_ct, obj_object_id=addd.id)
                rel.from_date = address["fromdatestr"]
                rel.to_date = address["todatestr"]
                rel.save()


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
                    if json_file.stem in ["agencies", "inventories", "memberships", "parties"]:
                        mdbm.content_object = Institution.objects.create()
                        mdbm.save()
                    if json_file.stem in ["institutions"]:
                        mdbm.content_object = EducationType.objects.create()
                        mdbm.save()
                    if json_file.stem in ["employers"]:
                        mdbm.content_object = ProfessionType.objects.create()
                        mdbm.save()
                    if json_file.stem in ["specialareas"]:
                        mdbm.content_object = SpecialArea.objects.create()
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
                    case "employers":
                        mdbm.content_object.label=mdbm.data["fullname"]
                        mdbm.content_object.save()
                    case "specialareas":
                        mdbm.content_object.label = mdbm.data["fullname"]
                        mdbm.content_object.save()
        for mdbm in MongoDbModel.objects.filter(filename="photographers.json"):
            parse_photographer(mdbm)
