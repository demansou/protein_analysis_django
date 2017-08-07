from Bio import SeqIO
from django import forms
from django.utils import timezone

from .custom import large_file_hasher
from .models import Collection, Motif, Sequence


class CollectionAdminForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = "__all__"

    def save(self, commit=True, *args, **kwargs):
        # Save without committing.
        # Creates object with name and file.
        collection = super(CollectionAdminForm, self).save(commit=False)

        if not collection.pk:
            # Set fields.
            collection.pub_date = timezone.now()
            collection.collection_parsed = False
            collection.sequence_count = 0

            # Generate file hash.
            file_path = collection.collection_file.path
            collection_hash = large_file_hasher(file_path)

            # If file hash not found, save collection
            if Collection.objects.filter(collection_hash=collection_hash).count() == 0:
                collection.collection_hash = collection_hash
                collection.save()

        if collection.pk:
            if not collection.collection_parsed:
                for record in SeqIO.parse(collection.collection_file.path, 'fasta'):
                    sequence = Sequence.objects.create(
                        collection_fk=collection,
                        sequence_id=record.id,
                        sequence_name=record.name,
                        sequence=str(record.seq),
                    )
                    sequence.save()

                collection.collection_parsed = True
                collection.sequence_count = Sequence.objects.filter(collection_fk=collection).count()

            collection.save()

        return collection


class CollectionForm(forms.Form):
    collections = forms.ModelMultipleChoiceField(
        label='Select Collections For Analysis',
        queryset=Collection.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    def as_bootstrap(self):
        return self._html_output(
            normal_row='<div class="col-xs-3"><li class="list-group-item">%(html_class_attr)s>%(label)s %(field)s%(help_text)s</li></div>',
            error_row='<div class="alert alert-danger">%s</div>',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=True
        )



class MotifForm(forms.Form):
    fields = forms.ModelMultipleChoiceField(queryset=Motif.objects.all())
