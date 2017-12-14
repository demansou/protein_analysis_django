from django.urls import path

from . import views

app_name = 'protein_analysis_tool'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('select_collections/', views.select_collections_view, name='select-collections'),
    path('select_motifs/', views.select_motifs_view, name='select-motifs'),
    path('define_parameters/', views.define_parameters_view, name='define-parameters'),
    path('process_query/', views.process_query_view, name='process-query'),
    path('process_all_queries/', views.process_all_queries_view, name='process-all-queries'),
    path('all_queries/', views.all_queries_view, name='all-queries'),
    path('results/<int:result_id>/', views.view_query_result, name='view-single-result'),
]
