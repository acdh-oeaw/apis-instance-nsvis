from apis_acdhch_default_settings.urls import urlpatterns

from django.urls import include, path

from apis_instance_nsvis.views import WrongAnnotationNumber

urlpatterns += [path("", include("apis_acdhch_django_invite.urls"))]
urlpatterns += [path("", include("django_interval.urls"))]
urlpatterns += [path("", include("apis_acdhch_django_auditlog.urls")),]

urlpatterns += [path("apis/apis_instance_nsvis.annotation/wrongnumberofauthors", WrongAnnotationNumber.as_view(), name="wrongnumberofauthors")]
