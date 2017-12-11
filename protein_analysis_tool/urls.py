from django.conf.urls import url

from . import views

app_name = 'protein_analysis_tool'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^select_collections/$', views.select_collections_view, name='select-collections'),
    url(r'^select_motifs/$', views.select_motifs_view, name='select-motifs'),
    url(r'^define_parameters/$', views.define_parameters_view, name='define-parameters'),
    url(r'^process_query/$', views.process_query_view, name='process-query'),
    url(r'^process_all_queries/$', views.process_all_queries_view, name='process-all-queries'),
    url(r'^all_queries/$', views.all_queries_view, name='all-queries'),
]
