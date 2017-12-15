from django.db import models
from django.core.files.storage import FileSystemStorage

from protein_analysis_django.settings import MEDIA_ROOT

fs = FileSystemStorage(location=MEDIA_ROOT)


class Collection(models.Model):
    """
    Collection name information and file storage.
    """
    collection_name = models.CharField(max_length=128)
    collection_file = models.FileField(storage=fs)
    collection_hash = models.CharField(max_length=16, unique=True)
    pub_date = models.DateTimeField('Date Published')
    collection_parsed = models.BooleanField(default=False)
    sequence_count = models.IntegerField(default=0)

    def __str__(self):
        return self.collection_name


class Sequence(models.Model):
    """
    Collection sequences.
    """
    collection_fk = models.ForeignKey(Collection, on_delete=models.CASCADE)
    sequence_id = models.CharField(max_length=256)
    sequence_name = models.CharField(max_length=256)
    sequence = models.CharField(max_length=4096)

    def __str__(self):
        return self.sequence_name


class Motif(models.Model):
    """
    Motif to search for in sequences.
    """
    motif = models.CharField(max_length=16)

    def __str__(self):
        return self.motif


class Query(models.Model):
    """
    Combination of Collection and Motif.
    """
    collection_fk = models.ForeignKey(Collection, on_delete=models.CASCADE)
    motif_fk = models.ForeignKey(Motif, on_delete=models.CASCADE)
    min_num_motifs_per_sequence = models.IntegerField()
    max_char_distance_between_motifs = models.IntegerField()
    query_is_finished = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            'collection_fk',
            'motif_fk',
            'min_num_motifs_per_sequence',
            'max_char_distance_between_motifs',
        )

    def __str__(self):
        return '{collection} -> {motif}'.format(collection=self.collection_fk, motif=self.motif_fk)


class QuerySequence(models.Model):
    """
    Combination of Query and Sequence.
    """
    query_fk = models.ForeignKey(Query, on_delete=models.CASCADE)
    sequence_fk = models.ForeignKey(Sequence, on_delete=models.CASCADE)
    is_match = models.BooleanField(default=False)
    matches = models.CharField(max_length=4096)

    class Meta:
        unique_together = (
            'query_fk',
            'sequence_fk',
        )

    def __str__(self):
        return '{motif} -> {matches}'.format(motif=self.sequence_fk, matches=self.matches)
