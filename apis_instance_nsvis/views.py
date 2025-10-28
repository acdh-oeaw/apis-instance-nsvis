from collections import defaultdict
from django.db.models import Count
from django.contrib.postgres.aggregates import ArrayAgg

from django.views.generic.base import TemplateView
from apis_instance_nsvis.models import Annotation
from apis_instance_nsvis.tables import AnnotationAuthorsTable, AnnotationReportsTable, AnnotationPhotographersTable, AnnotationAgenciesTable
from apis_core.generic.views import List
from django.urls import reverse
from django.shortcuts import redirect
from django.forms import modelformset_factory
from apis_instance_nsvis.forms import AnnotationForm
from apis_instance_nsvis.utils import Magazines


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


class AnnotationMagazinesView(TemplateView):
    template_name = "apis_instance_nsvis/annotation_magazines.html"

    def get_context_data(self, magazine=None, issue=None):
        ctx = super().get_context_data()
        ctx["magazines_container"] = Magazines()
        ctx["magazine"] = magazine
        ctx["issue"] = issue
        return ctx


class AnnotationPageView(TemplateView):
    template_name = "apis_instance_nsvis/annotation_page.html"

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.image = self.request.GET.get("image", None)
        self.formset = modelformset_factory(
            Annotation,
            form=AnnotationForm,
            fields="__all__",
            can_delete=True,
            extra=0,
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["image"] = self.image
        ctx["formset"] = kwargs.pop(
            "formset",
            self.formset(
                queryset=Annotation.objects.filter(image=self.image),
                form_kwargs={"image": self.image},
            ),
        )
        return ctx

    def post(self, *args, **kwargs):
        formset = self.formset(self.request.POST, form_kwargs={"image": self.image})
        if formset.is_valid():
            formset.save()
        else:
            return self.render_to_response(self.get_context_data(formset=formset))
        return redirect(reverse("annotationpage") + "?" + self.request.GET.urlencode())
