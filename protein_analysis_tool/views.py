from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.views import generic

from .forms import DefineParametersForm
from .models import Collection, Motif, Query


class IndexView(generic.TemplateView):
    template_name = 'protein_analysis_tool/index.html'


def select_collections_view(request):
    if request.POST:
        collection_list = request.POST.getlist('collection_group[]', False)

        # re-render form in case of empty list
        if not collection_list:
            pass

        # set session data
        request.session['collection_list'] = collection_list

        # redirect to next form
        return HttpResponseRedirect('/select_motifs/')

    # get list of objects or send HTTP 404
    collection_list = get_list_or_404(Collection, sequence_count__gte=1)

    # create context dictionary
    context = {
        'collections': collection_list,
    }

    # render form
    return render(request, 'protein_analysis_tool/select_collections.html', context=context)


def select_motifs_view(request):
    if request.POST:
        motif_list = request.POST.getlist('motif_group[]', False)

        # re-render form in case of empty list
        if not motif_list:
            pass

        # set session data
        request.session['motif_list'] = motif_list

        # redirect to next form
        return HttpResponseRedirect('/define_parameters/')

    # get list of selected collections from session or boolean False
    collection_list_cookie = request.session.get('collection_list', False)

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
        'motifs': motifs,
    }

    # render form
    return render(request, 'protein_analysis_tool/select_motifs.html', context=context)


def define_parameters(request):
    # get list of selected collections and motifs from session or boolean False
    collection_list_cookie = request.session.get('collection_list', False)
    motif_list_cookie = request.session.get('motif_list', False)

    # redirect to homepage if no cookies present
    if not collection_list_cookie or not motif_list_cookie:
        return HttpResponseRedirect('/')

    # if list, get each Collection from id
    collection_list = []
    for collection_id in collection_list_cookie:
        collection_list.append(Collection.objects.get(id=collection_id))

    # if list, get each Motif rom id
    motif_list = []
    for motif_id in motif_list_cookie:
        motif_list.append(Motif.objects.get(id=motif_id))

    # process HTTP POST request if needed
    if request.POST:
        # set form as filled object
        form = DefineParametersForm(request.POST)

        # check if form is valid
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
                        max_char_distance_between_motifs=form.cleaned_data['max_char_distance_between_motifs'],
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
                        max_char_distance_between_motifs=form.cleaned_data['max_char_distance_between_motifs'],
                    )

                    query_list.append(query.pk)

            # set cookie with list of query pks
            request.session['query_list'] = query_list

            return HttpResponseRedirect('/process_query/')

    # create context dictionary
    context = {
        'collection_list': collection_list,
        'motif_list': motif_list,
        'form': DefineParametersForm(),
    }

    return render(request, 'protein_analysis_tool/define_parameters.html', context=context)


def process_query(request):
    if request.POST:
        pass

    query_list_cookie = request.session.get('query_list', False)

    if not query_list_cookie:
        return HttpResponseRedirect('/')

    query_list = []
    for query_id in query_list_cookie:
        query_list.append(Query.objects.get(pk=query_id))

    context = {
        'query_list': query_list
    }

    return render(request, 'protein_analysis_tool/process_query.html', context=context)
