from collections import defaultdict
import httpx
import os

from django.core.management.base import BaseCommand

from apis_instance_nsvis.models import Annotation

labelstudio_uri = "https://label-studio.acdh-dev.oeaw.ac.at"
labelstudio_token = os.getenv("LABELSTUDIO_TOKEN", None)


def override(project, attribute):
    match project:
        case 69:
            if attribute == "issue":
                return "Wiener Illustrierte vom 23.11.1944"
    return None


class Command(BaseCommand):
    help = "Import data from LabelStudio Export"

    def handle(self, *args, **options):
        projects = [45, 48, 49, 50, 51, 52, 55, 56, 58, 63, 64, 65, 66, 69, 70, 71, 77, 78, 79, 80, 81, 82, 83]
        ann_ids = []
        if labelstudio_token:
            headers = {"Authorization": f"Token {labelstudio_token}"}
            for project in projects:
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
                    for ann in annotations:
                        annotation, created = Annotation.objects.get_or_create(lst_task_id=task_id, lst_annotation_id=annotations[ann]["annotation"], lst_result_id=ann)
                        ann_ids.append(annotation.id)
                        annotation.data = annotations[ann]
                        annotation.image = task["data"]["image"]
                        annotation.issue = override(project, "issue") or task["data"]["issue"]
                        annotation.save()
        Annotation.objects.exclude(id__in=ann_ids).delete()
        for ann in Annotation.objects.all():
            ann.author = next(iter(ann.data.get("Author", [])), "").splitlines()
            ann.caption = next(iter(ann.data.get("Caption", [])), None)
            ann.title = next(iter(ann.data.get("Title", [])), None)

            dargestelltes = ann.data.get("Dargestelltes", [])
            ann.depicted = list(set([x for xs in dargestelltes for x in xs]))
            ann.location = next(iter(ann.data.get("OrtInput", [])), None)

            thema = ann.data.get("Thema", [])
            ann.topic = list(set([x for xs in thema for x in xs]))
            ann.other = next(iter(ann.data.get("Sonstiges", [])), None)

            ann.save()
