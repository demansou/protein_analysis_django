from django.contrib import admin

from .forms import CollectionAdminForm
from .models import Collection, Sequence, Motif, Query


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

admin.site.register(Query)
