from django.db import models


class Collection(models.Model):
    """
    Collection name information and file storage.
    """
    collection_name = models.CharField(max_length=128)
    collection_file = models.FileField()
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
    motif_name = models.CharField(max_length=32)
    motif = models.CharField(max_length=16)

    def __str__(self):
        return self.motif_name
