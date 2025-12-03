from apis_core.generic.tables import GenericTable
import django_tables2 as tables
from apis_instance_nsvis.models import Annotation


class AnnotationAuthorsTable(tables.Table):
    author = tables.TemplateColumn(template_code='<a href="{% url "apis_core:generic:list" "apis_instance_nsvis.annotation" %}?author={{ record.author|urlencode }}">{{ record.author }}</a>')
    count = tables.Column()
    ranking = tables.Column()

    def value_author(self, value, record):
        return value


class AnnotationReportsTable(tables.Table):
    title = tables.TemplateColumn(template_code='<a href="{% url "apis_core:generic:list" "apis_instance_nsvis.annotation" %}?title={{ record.title }}">{{ record.title }}</a>')
    count = tables.Column()
    authors = tables.Column(empty_values=())

    def value_title(self, value, record):
        return value

    def render_authors(self, value, record):
        authors = set()
        for author_list in Annotation.objects.values_list("author", flat=True).filter(id__in=record.get("ids", [])):
            for author in author_list:
                authors.add(author)
        return ", ".join(authors)


class AnnotationPhotographersTable(tables.Table):
    photographer = tables.TemplateColumn(template_code='<a href="{% url "apis_core:generic:list" "apis_instance_nsvis.annotation" %}?photographer={{ record.photographer|urlencode }}">{{ record.photographer }}</a>')
    count = tables.Column()
    ranking = tables.Column()

    def value_photographer(self, value, record):
        return value


class AnnotationAgenciesTable(tables.Table):
    agency = tables.TemplateColumn(template_code='<a href="{% url "apis_core:generic:list" "apis_instance_nsvis.annotation" %}?agency={{ record.agency|urlencode }}">{{ record.agency }}</a>')
    count = tables.Column()
    ranking = tables.Column()

    def value_agency(self, value, record):
        return value


class AnnotationTopicsTable(tables.Table):
    topic = tables.Column()
    count = tables.Column()


class AnnotationDepictedTable(tables.Table):
    depicted = tables.Column()
    count = tables.Column()
