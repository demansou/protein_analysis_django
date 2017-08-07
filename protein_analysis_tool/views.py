from django.views import generic

from .forms import CollectionForm, MotifForm


class IndexView(generic.TemplateView):
    template_name = 'protein_analysis_tool/index.html'


class CollectionFormView(generic.FormView):
    form_class = CollectionForm
    template_name = 'protein_analysis_tool/select_collections.html'
    success_url = '/select_motifs/'

