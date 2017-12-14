from celery import Celery
from ..models import Motif, Query, Sequence, QuerySequence
import json
import re

app = Celery('process_queue', broker='ampq://guest@localhost')


def motif_to_regex(motif):
    """

    :param motif:
    :return:
    """
    return re.compile(motif)


@app.task
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
        matches_objects = []

        # iterate over each sequence in list of sequences
        for match in motif_regex.finditer(sequence.sequence):

            # declare beginning of motif substring
            substr_start = int(match.start())

            # gather regex matches in substring
            substr_analysis = [m for m in motif_regex.finditer(
                sequence.sequence[substr_start:substr_start + query.max_char_distance_between_motifs])]

            if len(substr_analysis) >= query.min_num_motifs_per_sequence:
                matches_objects.append(substr_analysis)

        try:
            # attempt to add data to already existing querysequence row
            query_sequence = QuerySequence.objects.get(query_fk=query, sequence_fk=sequence)
            query_sequence.is_match = bool(len(matches_objects) > 0)
            query_sequence.matches = json.dumps(matches_objects)
            query_sequence.save()

        except QuerySequence.DoesNotExist:
            # create new querysequence row if match does not already exist
            QuerySequence.objects.create(
                query_fk=query,
                sequence_fk=sequence,
                is_match=bool(len(matches_objects) > 0),
                matches=json.dumps(matches_objects)
            )

    # update run query to be finished
    Query.objects.filter(pk=query_id).update(query_is_finished=True)
