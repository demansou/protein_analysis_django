from django.urls import path

from . import views

app_name = 'protein_analysis_tool'

urlpatterns = [
    # url config for homepage/form
    path('', views.index_form_view, name='index'),

    # url config for displaying/processing queries
    path('process_query/', views.process_query_view, name='process-query'),

    # url config for processing all queries
    path('process_all_queries/', views.process_all_queries_view, name='process-all-queries'),

    # url config for displaying results
    path('results/<int:result_id>/', views.view_query_result, name='view-single-result'),
]
