from apis_acdhch_default_settings.urls import urlpatterns

from django.urls import include, path

from apis_instance_nsvis import views

urlpatterns += [path("", include("apis_acdhch_django_invite.urls"))]
urlpatterns += [path("", include("django_interval.urls"))]
urlpatterns += [path("", include("apis_acdhch_django_auditlog.urls")),]

urlpatterns += [path("apis/apis_instance_nsvis.annotation/wrongnumberofauthors", views.WrongAnnotationNumber.as_view(), name="wrongnumberofauthors")]
urlpatterns += [path("apis/<contenttype:contenttype>/authors", views.AnnotationAuthorsView.as_view(), name="annotationsauthorsview")]
urlpatterns += [path("apis/<contenttype:contenttype>/reports", views.AnnotationReportsView.as_view(), name="annotationsreportsview")]
urlpatterns += [path("apis/<contenttype:contenttype>/photographers", views.AnnotationPhotographersView.as_view(), name="annotationsphotographersview")]
urlpatterns += [path("apis/<contenttype:contenttype>/agencies", views.AnnotationAgenciesView.as_view(), name="annotationsagenciesview")]
urlpatterns += [path("apis/apis_instance_nsvis.annotation/magazines/", views.AnnotationMagazinesView.as_view(), name="annotationmagazines")]
urlpatterns += [path("apis/apis_instance_nsvis.annotation/magazines/<str:magazine>/<str:issue>", views.AnnotationMagazinesView.as_view(), name="annotationmagazines")]
urlpatterns += [path("apis/apis_instance_nsvis.annotation/page/", views.AnnotationPageView.as_view(), name="annotationpage")]
