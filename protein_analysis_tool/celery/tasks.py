from celery import Celery
from ..models import Motif, Query, Sequence

app = Celery('process_queue', broker='ampq://guest@localhost')


@app.task
def task_process_query(query_id):
    """

    :param query_id:
    :return: 
    """

    # get query that is paired to query
    query = Query.objects.get(pk=query_id)

    if not query:
        return

    # get motif that is paired to query
    motif = Motif.objects.get(pk=query.motif_fk.pk)

    # get each sequence in the collection that is queried
    sequence_list = Sequence.objects.filter(collection_fk=query.collection_fk)

    # get motif

    # perform analysis on each sequence in
    for sequence in sequence_list:

        # if sequence has one motif, continue checking

        # get subsequence of sequence from first motif

        # check for frequency of motif.

        #if positive, record positions.

        # update database