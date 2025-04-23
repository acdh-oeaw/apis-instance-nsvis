from collections import defaultdict
import django_tables2 as tables

from django.views.generic.base import TemplateView
from apis_instance_nsvis.models import Annotation
from apis_instance_nsvis.tables import AnnotationAuthorsTable
from apis_core.generic.views import List


class WrongAnnotationNumber(TemplateView):
    template_name = "wrong_annotation_number.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        annotations = Annotation.objects.all().values("issue", "title", "id")
        annotation_reports = defaultdict(list)
        for annotation in annotations:
            if annotation.get("title", None) is not None:
                annotation_reports[(annotation.get("issue"), annotation.get("title"))].append(annotation["id"])
        for key, val in annotation_reports.copy().items():
            if len(val) == 1:
                del annotation_reports[key]

        ctx["data"] = []
        for key, val in annotation_reports.items():
            report_images_cnt = len(val)
            for image_id in val:
                annotation = Annotation.objects.get(id=image_id)
                if len(annotation.author) != 1 and len(annotation.author) != report_images_cnt:
                    ctx["data"].append({"annotation": annotation, "nr_anns": report_images_cnt})
        return ctx


class AnnotationAuthorsView(List):
    def get_table_class(self):
        return AnnotationAuthorsTable

    def get_table_data(self, *args, **kwargs):
        data = defaultdict(lambda: 0)
        for ann in self.get_queryset():
            for author in ann.author:
                data[author] += 1
        return [{"author": key, "count": value} for key, value in data.items()]
