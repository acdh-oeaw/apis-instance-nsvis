from django.contrib import admin


from apis_instance_nsvis.models import Person, Place, Institution, MongoDbModel


@admin.register(Person, Place, Institution, MongoDbModel)
class NsvisAdmin(admin.ModelAdmin):
    pass
