from django.shortcuts import render
from django.views import generic

from .models import Collection


class IndexView(generic.TemplateView):
    template_name = 'protein_analysis_tool/index.html'


def select_collections(request):
    if request.method == 'POST':
        # TODO: save primary keys, redirect to 'select_motif(s)'
        pass

    collections = Collection.objects.all()
    return render(request, 'protein_analysis_tool/select_collections.html', context={'collections': collections})
