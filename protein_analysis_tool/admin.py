from django.contrib import admin

from .models import Collection, Sequence, Motif


class CollectionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Collection File Information', {
            'fields': [
                'collection_name',
                'collection_file',
            ],
        }),
    ]

    list_display = ['collection_name', 'collection_file', 'collection_hash', 'pub_date', 'collection_parsed']

admin.site.register(Collection, CollectionAdmin)
admin.site.register(Sequence)
admin.site.register(Motif)
