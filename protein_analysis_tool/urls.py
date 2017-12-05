from django.conf.urls import url

from . import views

app_name = 'protein_analysis_tool'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^select_collections/$', views.select_collections_view, name='select-collections'),
    url(r'^select_motifs/$', views.select_motifs_view, name='select-motifs'),
    url(r'^define_parameters/$', views.define_parameters, name='define-parameters'),
    url(r'^process_query/$', views.process_query, name='process-query'),
    url(r'^all_queries/$', views.all_queries, name='all-queries'),
]
