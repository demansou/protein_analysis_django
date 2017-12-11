from django.views import generic

from .views_controller import update_request_and_redirect_to_motif_selection,\
    get_list_of_objects_and_render_collection_form, update_request_and_redirect_to_define_parameters,\
    get_list_of_motifs_and_render_motif_form, update_request_and_redirect_to_process_query,\
    get_selected_collections_and_motifs_and_render_parameters_form,\
    get_selected_queries_and_render_process_query_http_get, get_all_queries_and_render_all,\
    process_single_query


class IndexView(generic.TemplateView):
    template_name = 'protein_analysis_tool/index.html'


def select_collections_view(request):
    if request.POST:
        return update_request_and_redirect_to_motif_selection(request)

    return get_list_of_objects_and_render_collection_form(request)


def select_motifs_view(request):
    if request.POST:
        return update_request_and_redirect_to_define_parameters(request)

    return get_list_of_motifs_and_render_motif_form(request)


def define_parameters(request):
    if request.POST:
        return update_request_and_redirect_to_process_query(request)

    return get_selected_collections_and_motifs_and_render_parameters_form(request)


def process_query(request):
    if request.POST:
        return process_single_query(request)

    return get_selected_queries_and_render_process_query_http_get(request)


def all_queries(request):
    if request.POST:
        return process_single_query(request)

    return get_all_queries_and_render_all(request)