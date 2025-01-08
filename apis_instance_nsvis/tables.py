import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable


class AnnotationTable(AbstractEntityTable):
    labelstudio = tables.TemplateColumn(template_name="columns/labelstudio_link.html")
