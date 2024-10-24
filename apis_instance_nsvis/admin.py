from django.contrib import admin


from apis_instance_nsvis.models import Person, Place, Institution


@admin.register(Person, Place, Institution)
class NsvisAdmin(admin.ModelAdmin):
    pass
