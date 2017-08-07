from django.conf.urls import url

from . import views

app_name = 'protein_analysis_tool'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^select_collections/$', views.CollectionFormView.as_view(), name='select-collections'),
]
