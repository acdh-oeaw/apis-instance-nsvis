from django.db.models import Q
from django_filters import UnknownFieldBehavior, FilterSet, MultipleChoiceFilter
from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
from apis_instance_nsvis.models import Annotation


class CustomMultipleChoiceFilter(MultipleChoiceFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra["choices"] = self.get_choices()

    def get_choices(self):
        choices = set()
        for value in Annotation.objects.exclude(Q(**{f"{self.field_name}__isnull": True})).values_list(self.field_name, flat=True):
            for val in value:
                choices.add((val, val))
        return choices

    def filter(self, qs, value):
        q = Q()
        for val in value:
            q |= Q(**{f"{self.field_name}__contains": [val]})
        return qs.filter(q)


class AnnotationFilterSet(FilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        unknown_field_behavior = UnknownFieldBehavior.IGNORE
        fields = {"caption": ["icontains"], "title": ["icontains"], "location": ["icontains"], "other": ["icontains"]}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["author"] = CustomMultipleChoiceFilter(field_name="author")
        self.filters["topic"] = CustomMultipleChoiceFilter(field_name="topic")
        self.filters["depicted"] = CustomMultipleChoiceFilter(field_name="depicted")
