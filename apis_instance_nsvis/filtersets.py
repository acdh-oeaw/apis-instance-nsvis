from django.db.models import Q
from django.forms.widgets import CheckboxInput
from django_filters import UnknownFieldBehavior, FilterSet, MultipleChoiceFilter, BooleanFilter
from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
from apis_instance_nsvis.models import Annotation


class PersonFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        unknown_field_behavior = UnknownFieldBehavior.IGNORE


class CustomMultipleChoiceFilter(MultipleChoiceFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra["choices"] = self.get_choices()

    def get_choices(self):
        choices = set()
        for value in Annotation.objects.exclude(Q(**{f"{self.field_name}__isnull": True})).values_list(self.field_name, flat=True):
            for val in value:
                choices.add(val)
        choices = sorted(choices)
        return list(zip(choices, choices))

    def filter(self, qs, value):
        q = Q()
        for val in value:
            q |= Q(**{f"{self.field_name}__contains": [val]})
        return qs.filter(q)


class IssueFilter(MultipleChoiceFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra["choices"] = self.get_choices()

    def get_choices(self):
        issues = sorted(Annotation.objects.values_list(self.field_name, flat=True).distinct())
        return zip(issues, issues)

    def filter(self, qs, value):
        q = Q()
        for val in value:
            q |= Q(**{f"{self.field_name}__contains": val})
        return qs.filter(q)


class MagazineFilter(IssueFilter):
    def get_choices(self):
        issues = sorted(Annotation.objects.values_list(self.field_name, flat=True).distinct())
        issues = [issue.split(" vom ") for issue in issues]
        issues = {issue[0] for issue in issues}
        return zip(issues, issues)


class InternalCommentExistsFilter(BooleanFilter):
    def filter(self, qs, value):
        if value:
            return qs.filter(internal_comment__isnull=not value)
        return qs


class MultipleAuthors(BooleanFilter):
    def filter(self, qs, value):
        if value:
            return qs.filter(author__len__gt=1)
        return qs


class AnnotationFilterSet(FilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        unknown_field_behavior = UnknownFieldBehavior.IGNORE
        fields = {"caption": ["icontains"], "title": ["icontains"], "location": ["icontains"], "other": ["icontains"]}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["issue"] = IssueFilter(field_name="issue")
        self.filters["magazine"] = MagazineFilter(field_name="issue")
        self.filters["author"] = CustomMultipleChoiceFilter(field_name="author")
        self.filters["topic"] = CustomMultipleChoiceFilter(field_name="topic")
        self.filters["depicted"] = CustomMultipleChoiceFilter(field_name="depicted")
        self.filters["internal_comment"] = InternalCommentExistsFilter(widget=CheckboxInput)
        self.filters["multiple_authors"] = MultipleAuthors(widget=CheckboxInput)
