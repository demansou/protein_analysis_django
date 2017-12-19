from __future__ import absolute_import, unicode_literals
from celery import shared_task
from protein_analysis_tool.models import Query, Sequence, QuerySequence
import json
import re


def motif_to_regex(motif):
    """

    :param motif:
    :return:
    """
    return re.compile(motif)


@shared_task
def task_process_all_queries():
    # put all un-finished queries in a iterable list
    query_list = Query.objects.filter(query_is_finished=False)

    # iterate through each query in list
    for query in query_list:
        # push to celery queue
        task_process_query(query.pk)


@shared_task
def task_process_query(query_id):
    """
    Takes query ID and processes each combination and either creates or updates a database row.
    :param query_id:
    :return: 
    """

    # get query that is paired to query
    query = Query.objects.get(pk=query_id)

    # exit task if no query
    if not query:
        return

    # get each sequence in the collection that is queried
    sequence_list = Sequence.objects.filter(collection_fk=query.collection_fk)

    # get motif that is paired to query
    motif_regex = motif_to_regex(query.motif_fk.motif)

    # perform analysis on each sequence in collection
    for sequence in sequence_list:
        regex_match_list = []

        # iterate over each sequence in list of sequences
        for match in motif_regex.finditer(sequence.sequence):
            substr_match_list = []

            # declare beginning of motif substring
            substr_start = int(match.start())

            # gather regex matches in substring
            substr_analysis = [m for m in motif_regex.finditer(
                sequence.sequence[substr_start:substr_start + query.max_char_distance_between_motifs])]

            # check that regex matches at least equal the minimum number of hits in the substring
            if len(substr_analysis) >= query.min_num_motifs_per_sequence:
                # if there are at least the minimum number of regex hits in the substring,
                # save each match as a dict
                for substr_match in substr_analysis:

                    substr = {
                        'start': substr_match.start(),
                        'group': substr_match.group(),
                        'span': (substr_start + substr_match.span()[0], substr_start + substr_match.span()[1])
                    }

                    substr_match_list.append(substr)

            regex_match_list.append(substr_match_list)

        try:
            # attempt to add data to already existing querysequence row
            query_sequence = QuerySequence.objects.get(query_fk=query, sequence_fk=sequence)
            query_sequence.is_match = bool(len(regex_match_list) > 0)
            query_sequence.matches = json.dumps(regex_match_list)
            query_sequence.save()

        except QuerySequence.DoesNotExist:
            # create new querysequence row if match does not already exist
            QuerySequence.objects.create(
                query_fk=query,
                sequence_fk=sequence,
                is_match=bool(len(regex_match_list) > 0),
                matches=json.dumps(regex_match_list)
            )

    # update run query to be finished
    Query.objects.filter(pk=query_id).update(query_is_finished=True)
