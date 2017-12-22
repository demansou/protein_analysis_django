from Bio import SeqIO
import json
import os
import tempfile
from django.utils import timezone

from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_list_or_404, render

from protein_analysis_tool.tasks import task_process_query, task_process_all_queries
from protein_analysis_django.settings import MEDIA_ROOT
from .custom import large_file_hasher, Singleton
from .models import Collection, Motif, Query, QuerySequence, Sequence


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


def reset_session_error_message(request):
    """

    :param request:
    :return:
    """
    try:
        del request.session['form_error']
    except KeyError:
        pass


def update_session_error_message(request, message):
    """

    :param request:
    :param message:
    :return:
    """
    request.session['form_error'] = message
    return request

#################
# POST REQUESTS #
#################


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
    # Celery task
    task_process_all_queries.delay()

    return HttpResponseRedirect('/all_queries/')


class IndexFormController(object, metaclass=Singleton):
    def __init__(self, request):
        """
        Initialize IndexForm controller with HTTP request.
        Perform form analysis.
        :param request:
        """
        self.request = request

        if self.request.POST:
            self.sequence_data_title = get_form_data_from_http_post(self.request, 'sequence_data_title')
            self.sequence_data = get_form_data_from_http_post(self.request, 'sequence_data')
            self.selected_collections = get_form_data_from_http_post_as_list(self.request, 'selected_collections[]')
            self.selected_motifs = get_form_data_from_http_post_as_list(self.request, 'selected_motifs[]')
            self.min_num_motifs = get_form_data_from_http_post(self.request, 'min_num_motifs')
            self.max_motif_range = get_form_data_from_http_post(self.request, 'max_motif_range')

    def generate_form(self):
        """
        Generate form
        :return:
        """
        collection_list = get_list_or_404(Collection, sequence_count__gte=1)
        motif_list = get_list_or_404(Motif)

        context = {
            'collection_list': collection_list,
            'motif_list': motif_list,
        }

        return render(self.request, 'protein_analysis_tool/form_index.html', context=context)

    def process_form(self):
        """
        Process form data
        :return:
        """
        # validate form fields
        self.check_form_data()

        # get selected collections (or empty list)
        selected_collections_objects = self.check_selected_collections()

        # get new collection from copy & pasted textarea data
        selected_collections_objects = self.check_copy_paste_data(selected_collections_objects)

        # get selected motifs (list cannot be empty)
        selected_motifs_objects = self.check_selected_motifs()

        # create QueryMotif database entries with data from form
        self.create_query_motifs(selected_collections_objects, selected_motifs_objects)

        return HttpResponseRedirect('/all_queries/')

    def check_form_data(self):
        """
        Handles form errors.
        :return:
        """
        reset_session_error_message(self.request)

        if len(self.sequence_data) == 0 and len(self.selected_collections) == 0:
            err = 'No sequence data selected AND no collections selected'
            self.request = update_session_error_message(self.request, err)
            return HttpResponseRedirect('/')

        if len(self.selected_motifs) == 0:
            err = 'No motifs selected'
            self.request = update_session_error_message(self.request, err)
            return HttpResponseRedirect('/')

        if int(self.min_num_motifs) < 2:
            err = 'Minimum number of motifs outside of allowed range'
            self.request = update_session_error_message(self.request, err)
            return HttpResponseRedirect('/')

        if int(self.max_motif_range) < 20 or int(self.max_motif_range) > 200:
            err = 'Maximum motif range outside of allowed range'
            self.request = update_session_error_message(self.request, err)
            return HttpResponseRedirect('/')

    def check_selected_collections(self):
        """
        Checks for selected collections in form. Returns list of objects or empty list.
        :return:
        """
        # if selected_collections is false (from import) return empty list
        if not self.selected_collections:
            return []

        return [Collection.objects.get(pk=int(c)) for c in self.selected_collections]

    def check_copy_paste_data(self, selected_collections_objects):
        """
        Checks for textarea input. Attempts to create new database entry with new collection data.
        :return:
        """
        # clear session error message if one present
        reset_session_error_message(self.request)

        # return only selected collections if no data input into textarea
        if len(str(self.sequence_data)) == 0:
            return selected_collections_objects

        # attempt to create new record or update previous record
        new_collection, created = Collection.objects.update_or_create(
            collection_name=str(self.sequence_data_title),
            pub_date=timezone.now(),
            collection_parsed=False,
            sequence_count=0
        )

        # create file object with textarea data
        content = ContentFile(str(self.sequence_data))

        # create new file with randomized name and save textarea data to field
        new_collection.collection_file.save(
            self.clean_path_from_filename(self.create_temp_filename()), content, save=True)

        # md5 hash saved file
        new_collection.collection_hash = large_file_hasher(new_collection.collection_file.path)

        # save file and hash to database
        new_collection.save()

        new_collection = self.parse_new_collection_file_data(new_collection)

        if not new_collection.pk:
            err = 'Failed to add new data to database. Cannot parse new collection data from text input'
            self.request = update_session_error_message(self.request, err)
            return HttpResponseRedirect('/')

        # return list of selected collections with new collection added
        selected_collections_objects.append(new_collection)

        return selected_collections_objects

    def parse_new_collection_file_data(self, new_collection):
        """

        :param new_collection:
        :return:
        """
        # clear session error message if one present
        reset_session_error_message(self.request)

        # iterate through fasta file and update record if exists with current collection as FK or create otherwise
        for record in SeqIO.parse(new_collection.collection_file.path, 'fasta'):
            Sequence.objects.update_or_create(
                collection_fk=new_collection,
                sequence_id=record.id,
                sequence_name=str(record.name),
                sequence=str(record.seq)
            )

        # set collection to parsed
        new_collection.collection_parsed = True

        # get count of sequences related to collection after update
        new_collection.sequence_count = Sequence.objects.filter(collection_fk=new_collection).count()

        # save changes to collection
        new_collection.save()

        if not Collection.objects.get(pk=new_collection.pk).collection_parsed:
            err = 'Error: Collection not parsed.'
            self.request = update_session_error_message(self.request, err)
            return HttpResponseRedirect('/')

        return new_collection



    def check_selected_motifs(self):
        """
        Checks for selected motifs in form. Returns list of objects.
        Cannot be empty because form requires at least one motif to process form.
        :return:
        """
        return [Motif.objects.get(pk=int(m)) for m in self.selected_motifs]

    def create_query_motifs(self, selected_collections_objects, selected_motifs_objects):
        """
        Create Query database entry for each collection/motif pair.
        :param selected_collections_objects:
        :param selected_motifs_objects:
        :return:
        """
        # clear session error message if one present
        reset_session_error_message(self.request)

        if len(selected_collections_objects) == 0 or len(selected_motifs_objects) == 0:
            err = 'Error occurred creating queries from data. # Collections: {0}, # Motifs: {1}'.format(
                len(selected_collections_objects),
                len(selected_motifs_objects)
            )
            update_session_error_message(self.request, err)
            return HttpResponseRedirect('/')

        for collection in selected_collections_objects:
            for motif in selected_motifs_objects:
                Query.objects.update_or_create(
                    collection_fk=collection,
                    motif_fk=motif,
                    min_num_motifs_per_sequence=int(self.min_num_motifs),
                    max_char_distance_between_motifs=int(self.max_motif_range)
                )

    @staticmethod
    def create_temp_filename():
        """
        Returns file name with full path.
        :return:
        """
        return tempfile.NamedTemporaryFile(
            suffix='.fasta',
            prefix='',
            dir=MEDIA_ROOT,
            delete=False
        ).name

    @staticmethod
    def clean_path_from_filename(file_name):
        """
        Returns file name from full path.
        :param file_name:
        :return:
        """
        return os.path.basename(file_name)


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

    try:
        del request.session['form_error']
    except KeyError:
        pass

    if len(sequence_data) == 0 and len(selected_collections) == 0:
        request.session['form_error'] = 'No sequence data selected AND no collections selected'
        return HttpResponseRedirect('/')

    if len(selected_motifs) == 0:
        request.session['form_error'] = 'No motifs selected'
        return HttpResponseRedirect('/')

    if int(min_num_motifs) < 2:
        request.session['form_error'] = 'Minimum number of motifs outside of allowed range'
        return HttpResponseRedirect('/')

    if int(max_motif_range) < 20 or int(max_motif_range) > 200:
        request.session['form_error'] = 'Maximum motif range outside of allowed range'
        return HttpResponseRedirect('/')

    if selected_collections:
        collection_list = [Collection.objects.get(pk=int(c)) for c in selected_collections]
    else:
        collection_list = []

    if len(sequence_data) > 0:
        if len(sequence_data_title) == 0:
            return HttpResponseRedirect('/')

        try:
            content = ContentFile(str(sequence_data))

            new_collection = Collection.objects.create(
                collection_name=str(sequence_data_title),
                pub_date=timezone.now(),
                collection_parsed=False,
                sequence_count=0
            )

            temp_file = tempfile.NamedTemporaryFile(
                suffix='.fasta',
                prefix='',
                dir=MEDIA_ROOT,
                delete=False
            )

            file_name = temp_file.name

            new_collection.collection_file.save(os.path.basename(file_name), content, save=True)
            new_collection.collection_hash = large_file_hasher(file_name)
            new_collection.save()

            for record in SeqIO.parse(new_collection.collection_file.path, 'fasta'):
                try:
                    sequence = Sequence.objects.create(
                        collection_fk=new_collection,
                        sequence_id=record.id,
                        sequence_name=record.name,
                        sequence=str(record.seq),
                    )
                    sequence.save()
                except IntegrityError:
                    continue

            new_collection.collection_parsed = True
            new_collection.sequence_count = Sequence.objects.filter(collection_fk=new_collection).count()
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


def process_query_view_controller(request):
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


def all_queries_view_controller(request):
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


def view_query_result_controller(request, result_id):
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
