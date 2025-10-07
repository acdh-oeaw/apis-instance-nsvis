from collections import defaultdict
from django.db.models import Count
from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg

from django.views.generic.base import TemplateView
from apis_instance_nsvis.models import Annotation
from apis_instance_nsvis.tables import AnnotationAuthorsTable, AnnotationReportsTable, AnnotationPhotographersTable, AnnotationAgenciesTable
from apis_core.generic.views import List
from pathlib import Path
import json

from apis_instance_nsvis.forms import NsvisImageAnnotationForm


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


class AnnotationFilterView(List):
    def get_table_class(self):
        return self.table_class

    def get_table_data(self, *args, **kwargs):
        filterset_class = self.get_filterset_class()
        kwargs = self.get_filterset_kwargs(filterset_class)
        filterset = filterset_class(**kwargs)
        return filterset.qs


class AnnotationAuthorsView(AnnotationFilterView):
    table_class = AnnotationAuthorsTable

    def get_table_data(self, *args, **kwargs):
        data = defaultdict(lambda: {"count": 0, "ranking": 0})
        for ann in super().get_table_data(*args, **kwargs):
            for author in set(ann.author):
                data[author]["count"] += 1
                data[author]["ranking"] += ann.ranking
        return [{"author": key, **value} for key, value in data.items()]


class AnnotationPhotographersView(AnnotationFilterView):
    table_class = AnnotationPhotographersTable

    def get_table_data(self, *args, **kwargs):
        data = defaultdict(lambda: {"count": 0, "ranking": 0})
        for ann in super().get_table_data(*args, **kwargs):
            for photographer in set([entry["photographer"] for entry in ann.photographers]):
                data[photographer]["count"] += 1
                data[photographer]["ranking"] += ann.ranking
        return [{"photographer": key, **value} for key, value in data.items()]


class AnnotationAgenciesView(AnnotationFilterView):
    table_class = AnnotationAgenciesTable

    def get_table_data(self, *args, **kwargs):
        data = defaultdict(lambda: {"count": 0, "ranking": 0})
        for ann in super().get_table_data(*args, **kwargs):
            for agency in set([entry["agency"] for entry in ann.photographers]):
                data[agency]["count"] += 1
                data[agency]["ranking"] += ann.ranking
        return [{"agency": key, **value} for key, value in data.items()]


class AnnotationReportsView(List):
    def get_table_class(self):
        return AnnotationReportsTable

    def get_table_data(self, *args, **kwargs):
        return Annotation.objects.values("title").annotate(count=Count("title"), ids=ArrayAgg("id")).order_by().filter(count__gt=1)


class MagazinesView(TemplateView):
    template_name = "apis_instance_nsvis/custom_magazines.html"

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        magazine_file = getattr(settings, "MAGAZINE_FILE", None)
        self.magazines = {}
        if magazine_file is not None:
            self.magazines = json.loads(Path(magazine_file).read_text())

    def get_context_data(self, title=None):
        ctx = super().get_context_data()
        ctx["magazines"] = self.magazines
        ctx["title"] = title
        return ctx


class PageView(TemplateView):
    template_name = "apis_instance_nsvis/custom_page.html"

    def get_context_data(self, title=None):
        ctx = super().get_context_data()
        ctx["image"] = self.request.GET.get("image", None)
        ctx["form"] = NsvisImageAnnotationForm()
        return ctx
