import json
import os
import tempfile
from django.utils import timezone

from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404, render

from protein_analysis_tool.tasks import task_process_query, task_process_all_queries
from protein_analysis_django.settings import MEDIA_ROOT
from .forms import DefineParametersForm
from .models import Collection, Motif, Query, QuerySequence


def get_form_data_from_http_post(request, key):
    """
    Returns form data from http post with key.
    :param request:
    :param key:
    :return:
    """
    return request.POST[key]


def get_form_data_from_http_post_as_list(request, key):
    """
    Returns form data list from http post with key.
    :param request:
    :param key:
    :return:
    """
    return request.POST.getlist(key, False)


def update_request_session_dict(request, key, value):
    """
    Sets session dict key value.
    :param request:
    :param key:
    :param value:
    :return:
    """
    request.session[key] = value


def get_session_data(request, key):
    """
    Gets session dict key value.
    :param request:
    :param key:
    :return:
    """
    return request.session.get(key, False)


def process_result_dict(result_dict):
    """

    :param result_dict:
    :return:
    """
    result_dict.matches = json.loads(result_dict.matches)
    return result_dict


def process_single_query(request):
    """

    :param request:
    :return:
    """

    query_id = get_form_data_from_http_post(request, 'query_id')

    if not query_id:
        pass

    # push to celery queue
    task_process_query.delay(query_id)

    return HttpResponseRedirect('/all_queries/')


def process_all_queries():
    """

    :return:
    """
    task_process_all_queries.delay()

    return HttpResponseRedirect('/all_queries/')


def display_query_result(request):
    """

    :param request:
    :return:
    """
    pass


#################
# POST REQUESTS #
#################


def update_request_and_redirect_to_motif_selection(request):
    """
    Gathers collections selected from collection selection form and adds them to session
    dictionary. Redirects page to motif selection form.
    :param request:
    :return:
    """

    collection_list = get_form_data_from_http_post_as_list(request, 'collection_group[]')

    # re-render form in case of empty list
    if not collection_list:
        pass

    # set session data
    update_request_session_dict(request, 'collection_list', collection_list)

    # redirect to next form
    return HttpResponseRedirect('/select_motifs/')


def update_request_and_redirect_to_define_parameters(request):
    """
    Takes selected motifs from form and adds them to session dictionary
    :param request:
    :return:
    """

    motif_list = get_form_data_from_http_post_as_list(request, 'motif_group[]')

    if not motif_list:
        pass

    update_request_session_dict(request, 'motif_list', motif_list)

    return HttpResponseRedirect('/define_parameters')


def update_request_and_redirect_to_process_query(request):
    """
    Creates queries with selected collections, motifs, and parameters
    :param request:
    :return:
    """

    # get list of selected collections and motifs from session
    collection_list_cookie = get_session_data(request, 'collection_list')
    motif_list_cookie = get_session_data(request, 'motif_list')

    # redirect to homepage if cookies not present
    if not collection_list_cookie or not motif_list_cookie:
        return HttpResponseRedirect('/')

    collection_list = []
    for collection_id in collection_list_cookie:
        collection_list.append(Collection.objects.get(id=collection_id))

    motif_list = []
    for motif_id in motif_list_cookie:
        motif_list.append(Motif.objects.get(id=motif_id))

    form = DefineParametersForm(request.POST)

    # check if the form is valid
    if form.is_valid():

        # create list to store query pks
        query_list = []

        # iterate through each combination of collection and motif from lists
        for collection in collection_list:
            for motif in motif_list:
                query = Query(
                    collection_fk=collection,
                    motif_fk=motif,
                    min_num_motifs_per_sequence=form.cleaned_data['min_num_motifs_per_sequence'],
                    max_char_distance_between_motifs=form.cleaned_data['max_char_distance_between_motifs']
                )

                # attempt to save each generated query
                # if already found in database will pass
                try:
                    query.save()
                except IntegrityError:
                    pass

                query = get_object_or_404(
                    Query,
                    collection_fk=collection,
                    motif_fk=motif,
                    min_num_motifs_per_sequence=form.cleaned_data['min_num_motifs_per_sequence'],
                    max_char_distance_between_motifs=form.cleaned_data['max_char_distance_between_motifs']
                )

                query_list.append(query.pk)

        # set cookie with list of query pks
        request.session['query_list'] = query_list

        return HttpResponseRedirect('/process_query/')


def index_form_process_controller(request):
    """

    :param request:
    :return:
    """

    sequence_data_title = get_form_data_from_http_post(request, 'sequence_data_title')
    sequence_data = get_form_data_from_http_post(request, 'sequence_data')
    selected_collections = get_form_data_from_http_post_as_list(request, 'selected_collections[]')
    selected_motifs = get_form_data_from_http_post_as_list(request, 'selected_motifs[]')
    min_num_motifs = get_form_data_from_http_post(request, 'min_num_motifs')
    max_motif_range = get_form_data_from_http_post(request, 'max_motif_range')

    if len(sequence_data) == 0 and len(selected_collections) == 0:
        return HttpResponseRedirect('/')

    if len(selected_motifs) == 0:
        return HttpResponseRedirect('/')

    if int(min_num_motifs) < 2:
        return HttpResponseRedirect('/')

    if int(max_motif_range) < 20 or int(max_motif_range) > 200:
        return HttpResponseRedirect('/')

    if selected_collections:
        collection_list = [Collection.objects.get(pk=int(c)) for c in selected_collections]
    else:
        collection_list = []

    if len(sequence_data) > 0:
        if len(sequence_data_title) == 0:
            return HttpResponseRedirect('/')

        content = ContentFile(str(sequence_data))

        try:
            new_collection = Collection.objects.create(
                collection_name=str(sequence_data_title),
                pub_date=timezone.now(),
                collection_parsed=False,
                sequence_count=0
            )

            file_name = tempfile.NamedTemporaryFile(
                prefix=new_collection.collection_name,
                suffix='.fasta',
                dir=MEDIA_ROOT
            ).name

            new_collection.collection_file.save(
                os.path.join(MEDIA_ROOT, file_name), content=content)

            new_collection.save()

            collection_list.append(new_collection)
        except IntegrityError:
            pass

    motif_list = [Motif.objects.get(pk=int(m)) for m in selected_motifs]

    for collection in collection_list:
        for motif in motif_list:
            try:
                Query.objects.create(
                    collection_fk=collection,
                    motif_fk=motif,
                    min_num_motifs_per_sequence=min_num_motifs,
                    max_char_distance_between_motifs=max_motif_range
                )
            except IntegrityError:
                continue

    return HttpResponseRedirect('/all_queries/')



################
# GET REQUESTS #
################


def index_form_view_controller(request):
    """

    :param request:
    :return:
    """

    collection_list = get_list_or_404(Collection, sequence_count__gte=1)

    motif_list = get_list_or_404(Motif)

    context = {
        'collection_list': collection_list,
        'motif_list': motif_list,
    }

    return render(request, 'protein_analysis_tool/form_index.html', context=context)


def get_list_of_objects_and_render_collection_form(request):
    """
    Gathers collections from database and renders collection selection form.
    :param request:
    :return:
    """

    # get list of collections from database
    collection_list = get_list_or_404(Collection, sequence_count__gte=1)

    # create context dictionary
    context = {
        'collections': collection_list
    }

    # render form
    return render(request, 'protein_analysis_tool/select_collections.html', context=context)


def get_list_of_motifs_and_render_motif_form(request):
    """
    Displays selected collections, gives list of motifs to select, and displays form.
    :param request:
    :return:
    """

    # get list of selected collections from session or boolean False
    collection_list_cookie = get_session_data(request, 'collection_list')

    # if no list, redirect to homepage
    if not collection_list_cookie:
        return HttpResponseRedirect('/')

    # if list, get each Collection from id
    collection_list = []
    for collection_id in collection_list_cookie:
        collection_list.append(Collection.objects.get(id=collection_id))

    # get motifs to choose from
    motifs = get_list_or_404(Motif)

    # create context dictionary
    context = {
        'collection_list': collection_list,
        'motifs': motifs
    }

    # render form
    return render(request, 'protein_analysis_tool/select_motifs.html', context=context)


def get_selected_collections_and_motifs_and_render_parameters_form(request):
    """
    Gets selected collections and motifs and renders the parameters input form.
    :param request:
    :return:
    """

    # get list of selected collections and motifs from session
    collection_list_cookie = get_session_data(request, 'collection_list')
    motif_list_cookie = get_session_data(request, 'motif_list')

    # redirect to homepage if cookies not present
    if not collection_list_cookie or not motif_list_cookie:
        return HttpResponseRedirect('/')

    collection_list = []
    for collection_id in collection_list_cookie:
        collection_list.append(Collection.objects.get(id=collection_id))

    motif_list = []
    for motif_id in motif_list_cookie:
        motif_list.append(Motif.objects.get(id=motif_id))

    # create context dictionary
    context = {
        'collection_list': collection_list,
        'motif_list': motif_list,
        'form': DefineParametersForm(),
    }

    return render(request, 'protein_analysis_tool/define_parameters.html', context=context)


def get_selected_queries_and_render_process_query_http_get(request):
    """
    In Process Query view, get list of queries entered this session.
    :param request:
    :return:
    """

    query_list_cookie = request.session.get('query_list', False)

    if not query_list_cookie:
        return HttpResponseRedirect('/')

    query_list = []
    for query_id in query_list_cookie:
        query_list.append(Query.objects.get(pk=query_id))

    context = {
        'query_list': query_list,
    }

    return render(request, 'protein_analysis_tool/process_query.html', context=context)


def get_all_queries_and_render_all(request):
    """
    View all queries.
    :param request:
    :return:
    """

    # get all queries and format as list
    query_list = [query for query in Query.objects.all()]

    # create context
    context = {
        'query_list': query_list,
    }

    # render process_query page with all queries
    return render(request, 'protein_analysis_tool/process_query.html', context=context)


def get_selected_result_and_render(request, result_id):
    """

    :param request:
    :param result_id:
    :return:
    """

    # get results list and process matches to encode as json
    result_list = [process_result_dict(query_sequence) for query_sequence
                   in QuerySequence.objects.filter(query_fk_id=result_id)]

    motif = Query.objects.get(pk=result_id).motif_fk.motif

    # create context
    context = {
        'result_list': result_list,
        'motif': motif,
    }

    # return results page with list of results
    return render(request, 'protein_analysis_tool/result_viewer.html', context=context)
