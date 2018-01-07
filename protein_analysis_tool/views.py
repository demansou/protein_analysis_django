from .views_controller import IndexFormController, ProcessQueryController, ResultsController


def index_form_view(request):
    """
    Connects to controller for displaying
    and processing motif analysis form.
    :param request:
    :return:
    """
    controller = IndexFormController(request)

    if request.method == 'POST':
        return controller.process_form()

    return controller.generate_form()


def process_query_view(request):
    """
    Connects to controller for displaying
    and processing commands to process queries.
    :param request:
    :return:
    """
    controller = ProcessQueryController(request)

    if request.method == 'POST':
        return controller.process_query()

    return controller.display_queries()


def process_all_queries_view(request):
    """
    Sends a command to process all queries.
    :param request:
    :return:
    """
    if request.method == 'POST':
        pass

    # Static method. Does not initialize an instance of controller.
    return ProcessQueryController.process_all_queries()


def view_query_result(request, result_id):
    """
    Connects to a controller to gather and display
    results for a specific query.
    :param request:
    :param result_id:
    :return:
    """
    controller = ResultsController(request)

    if request.method == 'POST':
        pass

    return controller.display_results(result_id)
