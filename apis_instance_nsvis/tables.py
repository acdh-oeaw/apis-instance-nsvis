import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from apis_core.relations.tables import RelationsListTable


class AnnotationTable(AbstractEntityTable):
    labelstudio = tables.TemplateColumn(template_name="columns/labelstudio_link.html")
    topic = tables.TemplateColumn(template_code="{{ record.topic|join:', ' }}")
    depicted = tables.TemplateColumn(template_code="{{ record.depicted|join:', ' }}")

    class Meta(AbstractEntityTable.Meta):
        fields = ["caption"]


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


class PersonEducationTypeRelationsTable(TimespanTable):
    details = tables.Column()

    class Meta(TimespanTable.Meta):
        sequence = (list(TimespanTable.Meta.sequence)[:-5] + ["details"] + list(TimespanTable.Meta.sequence)[-5:])


class PersonProfessionTypeRelationsTable(TimespanTable):
    details = tables.Column()

    class Meta(TimespanTable.Meta):
        sequence = (list(TimespanTable.Meta.sequence)[:-5] + ["details"] + list(TimespanTable.Meta.sequence)[-5:])


class PersonPlaceRelationsTable(TimespanTable):
    class Meta(TimespanTable.Meta):
        ...
