from django.contrib import admin

from .models import Collection, Sequence, Motif


admin.site.register(Collection)
admin.site.register(Sequence)
admin.site.register(Motif)
