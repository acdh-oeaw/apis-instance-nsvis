from collections import defaultdict
import itertools
import httpx
import os

from django.core.management.base import BaseCommand

from apis_instance_nsvis.models import Annotation
from apis_core.collections.models import SkosCollection

labelstudio_uri = "https://label-studio.acdh-dev.oeaw.ac.at"
labelstudio_token = os.getenv("LABELSTUDIO_TOKEN", None)
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
    fotographer = None
    korr_str = orig_str
    for row in author_data:
        if row["Author"].strip() == orig_str:
            korr_str = row.get("Korrektur") or orig_str
            agency = row["Agentur"]
            fotographer = row["Fotograf:in"]
    if not fotographer and not agency:
        fotographer = korr_str
    return korr_str, fotographer, agency


class Command(BaseCommand):
    help = "Import data from LabelStudio Export"

    def handle(self, *args, **options):
        get_author_data()
        first_batch_projects = [45, 48, 49, 50, 51, 52, 55, 56, 58, 63, 64, 65, 66, 69, 70, 71, 77, 78, 79, 80, 81, 82, 83, 99, 100]
        projects = []
        ann_ids = []
        if labelstudio_token:
            headers = {"Authorization": f"Token {labelstudio_token}"}
            for project in projects + first_batch_projects:
                endpoint = f"{labelstudio_uri}/api/projects/{project}/export?exportType=JSON"
                data = httpx.get(endpoint, headers=headers).json()
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
                    for ann in annotations:
                        annotation, created = Annotation.objects.get_or_create(lst_task_id=task_id, lst_annotation_id=annotations[ann]["annotation"], lst_result_id=ann)
                        ann_ids.append(annotation.id)
                        annotation.data = annotations[ann]
                        annotation.image = task["data"]["image"]
                        annotation.issue = override(project, "issue") or task["data"]["issue"]
                        annotation.save()
        # Annotation.objects.exclude(data__project_id__in=first_batch_projects).exclude(id__in=ann_ids).delete()
        Annotation.objects.exclude().exclude(id__in=ann_ids).delete()
        first_batch_collection, _ = SkosCollection.objects.get_or_create(name="Annotations: first batch")
        for ann in Annotation.objects.all():
            if ann.data["project_id"] in first_batch_projects:
                first_batch_collection.add(ann)
            authors = next(iter(ann.data.get("Author", [])), "").splitlines()
            if not authors:
                authors = ["unbekannt"]
            authors = [get_fixed_data(author.strip()) for author in authors]
            ann.author = [author[0] for author in authors]
            fotographers = []
            for orig_author, fotographer, agency in authors:
                if fotographer:
                    fotographer = fotographer.split("@")
                else:
                    fotographer = [None]
                if agency:
                    agency = agency.split("@")
                else:
                    agency = [None]
                fotographer = [f.strip() if f else f for f in fotographer]
                agency = [a.strip() if a else a for a in agency]
                for comb in list(itertools.product(fotographer, agency)):
                    fotographers.append({"fotographer": comb[0], "agency": comb[1]})
            ann.fotographers = fotographers

            ann.caption = next(iter(ann.data.get("Caption", [])), None)
            ann.title = next(iter(ann.data.get("Title", [])), None)

            dargestelltes = ann.data.get("Dargestelltes", [])
            ann.depicted = list(set([x for xs in dargestelltes for x in xs]))
            ann.location = next(iter(ann.data.get("OrtInput", [])), None)

            thema = ann.data.get("Thema", [])
            ann.topic = list(set([x for xs in thema for x in xs]))
            ann.other = next(iter(ann.data.get("Sonstiges", [])), None)
            ann.internal_comment = next(iter(ann.data.get("InternalComment", [])), None)

            ann.save()
            ann.fetch_and_upload()
