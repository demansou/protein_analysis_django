from .views_controller import update_request_and_redirect_to_motif_selection,\
    get_list_of_objects_and_render_collection_form, update_request_and_redirect_to_define_parameters,\
    get_list_of_motifs_and_render_motif_form, update_request_and_redirect_to_process_query,\
    get_selected_collections_and_motifs_and_render_parameters_form,\
    get_selected_queries_and_render_process_query_http_get, get_all_queries_and_render_all,\
    process_single_query, process_all_queries, get_selected_result_and_render, index_form_view_controller


def index_form_view(request):
    if request.POST:
        pass

    return index_form_view_controller(request)


def select_collections_view(request):
    if request.POST:
        return update_request_and_redirect_to_motif_selection(request)

    return get_list_of_objects_and_render_collection_form(request)


def select_motifs_view(request):
    if request.POST:
        return update_request_and_redirect_to_define_parameters(request)

    return get_list_of_motifs_and_render_motif_form(request)


def define_parameters_view(request):
    if request.POST:
        return update_request_and_redirect_to_process_query(request)

    return get_selected_collections_and_motifs_and_render_parameters_form(request)


def process_query_view(request):
    if request.POST:
        return process_single_query(request)

    return get_selected_queries_and_render_process_query_http_get(request)


def all_queries_view(request):
    if request.POST:
        return process_single_query(request)

    return get_all_queries_and_render_all(request)


def process_all_queries_view(request):
    if request.POST:
        pass

    return process_all_queries(request)


def view_query_result(request, result_id):
    if request.POST:
        pass

    return get_selected_result_and_render(request, result_id)

