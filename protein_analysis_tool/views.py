from django.shortcuts import get_list_or_404, render
from django.views import generic

from .models import Collection, Motif


class IndexView(generic.TemplateView):
    template_name = 'protein_analysis_tool/index.html'


def select_collections_view(request):
    if request.POST:
        collection_list = request.POST.get('collection_group[]')

        # re-render form in case of empty list
        if not collection_list:
            pass

        # save list for passing into html
        context = {
            'collection_list': collection_list,
        }

        # render next form
        return render(request, 'protein_analysis_tool/select_motifs.html', context)

    # get list of objects or send HTTP 404
    collection_list = get_list_or_404(Collection, sequence_count__gte=1)

    # create context dictionary
    context = {
        'collections': collection_list,
    }

    # render form
    return render(request, 'protein_analysis_tool/select_collections.html', context=context)


def select_motifs_view(request):
    if request.POST:
        pass

    collection_list = request.GET.get('collection_list')

    motifs = Motif.objects.all()

    context = {
        'collection_list': collection_list,
        'motifs': motifs,
    }

    return render(request, 'protein_analysis_tool/select_motifs.html', context=context)
