import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from apis_core.relations.tables import RelationsListTable


class AnnotationTable(AbstractEntityTable):
    labelstudio = tables.TemplateColumn(template_name="columns/labelstudio_link.html")


class TimespanTable(RelationsListTable):
    from_date = tables.Column(order_by="from_date_sort")
    to_date = tables.Column(order_by="to_date_sort")

    class Meta(RelationsListTable.Meta):
        sequence = (list(RelationsListTable.Meta.sequence)[:-3] + ["from_date", "to_date"] + list(RelationsListTable.Meta.sequence)[-3:])


class PersonAddressDataRelationsTable(TimespanTable):
    class Meta(TimespanTable.Meta):
        ...


class PersonInstitutionRelationsTable(TimespanTable):
    class Meta(TimespanTable.Meta):
        ...
