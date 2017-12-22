from .views_controller import all_queries_view_controller, process_all_queries, view_query_result_controller, \
    IndexFormController, ProcessQueryController, ResultsController


def index_form_view(request):
    controller = IndexFormController(request)

    if request.method == 'POST':
        return controller.process_form()

    return controller.generate_form()


def process_query_view(request):
    controller = ProcessQueryController(request)

    if request.method == 'POST':
        return controller.process_query()

    return controller.display_queries()


"""
def all_queries_view(request):
    if request.POST:
        return process_single_query(request)

    return all_queries_view_controller(request)
"""

"""
def process_all_queries_view(request):
    if request.method == 'POST':
        pass

    return process_all_queries()
"""

def view_query_result(request, result_id):
    controller = ResultsController(request)

    if request.method == 'POST':
        pass

    # return view_query_result_controller(request, result_id)
    return controller.display_results(result_id)
