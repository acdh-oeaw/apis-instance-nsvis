from collections import defaultdict
import itertools
import json
import httpx
import os
import pathlib
from django.utils.dateparse import parse_datetime
from simple_history.utils import get_history_model_for_model

from django.core.management.base import BaseCommand

from apis_instance_nsvis.models import Annotation
from apis_core.collections.models import SkosCollection

baserow_token = os.getenv("BASEROW_TOKEN", None)
baserow_db = os.getenv("BASEROW_DB", None)

author_data = []

def get_author_data():
    _next = f"https://baserow.acdh-dev.oeaw.ac.at/api/database/rows/table/{baserow_db}/?user_field_names=true&size=200"
    while _next:
        data = httpx.get(_next, headers={"Authorization": f"Token {baserow_token}"}, follow_redirects=True).json()
        author_data.extend(data["results"])
        _next = data["next"]

def override(project, attribute):
    match project:
        case 69:
            if attribute == "issue":
                return "Wiener Illustrierte vom 23.11.1944"
    return None

def get_fixed_data(orig_str):
    agency = None
    photographer = None
    korr_str = orig_str
    warreporter = False
    for row in author_data:
        if row["Author"].strip() == orig_str:
            korr_str = row.get("Korrektur") or orig_str
            agency = row["Agentur"]
            photographer = row["Fotograf:in"]
            warreporter = row["Kriegsberichter"]
    if not photographer and not agency:
        photographer = korr_str
    return korr_str, photographer, agency, warreporter


class Command(BaseCommand):
    help = "Import data from LabelStudio Export"

    def handle(self, *args, **options):
        changed_annotations = []
        for path in pathlib.Path("labelstudio_dump").iterdir():
            print(path)
            for file in path.glob("*.json"):
                project = file.name
                print(file)
                data = json.loads(file.read_text())
                for task in data:
                    task_id = task["id"]
                    annotations = defaultdict(dict)
                    for annotation in task.get("annotations", []):
                        for result in annotation.get("result", []):
                            match result["type"]:
                                case "rectangle":
                                    annotations[result["id"]] |= result["value"]
                                    annotations[result["id"]]["original_width"] = result["original_width"]
                                    annotations[result["id"]]["original_height"] = result["original_height"]
                                case "taxonomy":
                                    annotations[result["id"]][result["from_name"]] = result["value"]["taxonomy"]
                                case "textarea":
                                    annotations[result["id"]][result["from_name"]] = result["value"]["text"]
                            annotations[result["id"]]["annotation"] = annotation["id"]
                            annotations[result["id"]]["iiif_label"] = task["data"]["label"]
                            annotations[result["id"]]["project_id"] = project
                            annotations[result["id"]]["updated_at"] = annotation["updated_at"]
                    for ann in annotations:
                        updated = parse_datetime(annotations[ann]["updated_at"])

                        lst_attrs = {"lst_task_id": task_id, "lst_annotation_id": annotations[ann]["annotation"], "lst_result_id": ann}
                        try:
                            annotation = Annotation.objects.get(**lst_attrs)
                        except Annotation.DoesNotExist:
                            annotation = Annotation(**lst_attrs)
                            annotation.data = annotations[ann]
                            annotation.image = task["data"]["image"]
                            annotation.issue = override(project, "issue") or task["data"]["issue"]
                            annotation._history_date = updated
                            annotation.save()
                            changed_annotations.append(annotation.id)

                        last_db_update = None
                        try:
                            last_db_update = annotation.history.latest().history_date
                        except VersionAnnotation.DoesNotExist:
                            attributes = lst_attrs.copy()
                            attributes["data"] = annotation.data
                            attributes["image"] = annotation.image
                            attributes["issue"] = annotation.issue
                            attributes["history_date"] = updated
                            attributes["history_user"] = None
                            attributes["history_change_reason"] = ""
                            attributes["history_type"] = "+"
                            attributes["id"] = annotation.id
                            attributes["rootobject_ptr_id"] = annotation.id
                            VersionAnnotation.objects.create(**attributes)
                            last_db_update = updated
                            changed_annotations.append(annotation.id)

                        if last_db_update < updated:
                            annotation.data = annotations[ann]
                            annotation._history_date = updated
                            annotation.save()

        # update the data of the annotations that have been created or changed
        print(f"The following annotations are going to be udpated: {changed_annotations}")
        if changed_annotations:

            get_author_data()

            for ann in Annotation.objects.filter(id__in=changed_annotations):
                authors = next(iter(ann.data.get("Author", [])), "").splitlines()
                if not authors:
                    authors = ["unbekannt"]
                authors = [get_fixed_data(author.strip()) for author in authors]
                ann.author = [author[0] for author in authors]
                photographers = []
                for orig_author, photographer, agency, warreporter in authors:
                    if photographer:
                        photographer = photographer.split("@")
                    else:
                        photographer = [None]
                    if agency:
                        agency = agency.split("@")
                    else:
                        agency = [None]
                    photographer = [f.strip() if f else f for f in photographer]
                    agency = [a.strip() if a else a for a in agency]
                    for comb in list(itertools.product(photographer, agency)):
                        photographers.append({"photographer": comb[0], "agency": comb[1]})
                ann.warreporter = warreporter
                ann.photographers = photographers

                ann.caption = next(iter(ann.data.get("Caption", [])), None)
                ann.title = next(iter(ann.data.get("Title", [])), None)

                dargestelltes = ann.data.get("Dargestelltes", [])
                ann.depicted = sorted(list(set([x for xs in dargestelltes for x in xs])))
                ann.location = next(iter(ann.data.get("OrtInput", [])), None)

                thema = ann.data.get("Thema", [])
                ann.topic = sorted(list(set([x for xs in thema for x in xs])))
                ann.other = next(iter(ann.data.get("Sonstiges", [])), None)
                ann.internal_comment = next(iter(ann.data.get("InternalComment", [])), None)

                ann.save()
