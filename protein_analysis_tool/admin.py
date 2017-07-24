from Bio import SeqIO
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.html import format_html

from .models import Collection, Sequence, Motif


class CollectionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Collection File Information', {
            'fields': [
                'collection_name',
                'collection_file',
                'collection_hash',
                'collection_parsed',
                'pub_date',
            ],
        }),
    ]

    readonly_fields = [
        'collection_name',
        'collection_file',
        'collection_hash',
        'collection_parsed',
        'pub_date',
    ]

    list_display = [
        'collection_name',
        'collection_file',
        'collection_hash',
        'pub_date',
        'collection_parsed',
        'parse_file_action',
    ]

    def parse_file_action(self, obj):
        # TODO: render action button
        return format_html(
            '<a class="button" href="{}">Parse FASTA File</a>', reverse('admin:parse-file', args=[obj.pk]),
        )

    parse_file_action.short_description = 'Parse FASTA File?'

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            url(
                r'^(?P<collection_id>.+)/parse_file/$',
                self.admin_site.admin_view(self.process_parse_file),
                name='parse-file'
            ),
        ]

        return custom_urls + urls

    def process_parse_file(self, request, collection_id, *args, **kwargs):
        return self.process_action(
            request=request,
            collection_id=collection_id,
        )

    def process_action(self, request, collection_id):
        collection = self.get_object(request, collection_id)

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

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        return HttpResponseRedirect('/admin/protein_analysis_tool/', )


class SequenceAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Sequence Information', {
            'fields': [
                'collection_fk',
                'sequence_id',
                'sequence_name',
                'sequence'
            ],
        }),
    ]

    readonly_fields = [
        'collection_fk',
        'sequence_id',
        'sequence_name',
        'sequence',
    ]

    list_display = [
        'sequence_id',
        'sequence_name',
        'sequence',
    ]

admin.site.register(Collection, CollectionAdmin)
admin.site.register(Sequence, SequenceAdmin)
admin.site.register(Motif)
