from .views_controller import process_query_view_controller, all_queries_view_controller,\
    process_single_query, process_all_queries, view_query_result_controller, IndexFormController


def index_form_view(request):
    # if request.POST:
        # return index_form_process_controller(request)

    # return index_form_view_controller(request)
    return IndexFormController(request)


def process_query_view(request):
    if request.POST:
        return process_single_query(request)

    return process_query_view_controller(request)


def all_queries_view(request):
    if request.POST:
        return process_single_query(request)

    return all_queries_view_controller(request)


def process_all_queries_view(request):
    if request.POST:
        pass

    return process_all_queries()


def view_query_result(request, result_id):
    if request.POST:
        pass

    return view_query_result_controller(request, result_id)
