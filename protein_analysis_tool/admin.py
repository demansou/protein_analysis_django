from django.contrib import admin

from .forms import CollectionAdminForm
from .models import Collection, Sequence, Motif, Query, QuerySequence


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    form = CollectionAdminForm

    readonly_fields = [
        'pub_date',
        'collection_hash',
        'collection_parsed',
        'sequence_count',
    ]

    list_display = [
        'collection_name',
        'collection_file',
        'collection_hash',
        'collection_parsed',
        'sequence_count',
    ]


@admin.register(Sequence)
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


@admin.register(Motif)
class MotifAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Motif Information', {
            'fields': [
                'motif',
            ],
        }),
    ]


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Query Information', {
            'fields': [
                'collection_fk',
                'motif_fk',
                'min_num_motifs_per_sequence',
                'max_char_distance_between_motifs',
                'query_is_finished'
            ],
        }),
    ]

    readonly_fields = [
        'collection_fk',
        'motif_fk',
        'min_num_motifs_per_sequence',
        'max_char_distance_between_motifs',
        'query_is_finished',
    ]

admin.register(QuerySequence)
