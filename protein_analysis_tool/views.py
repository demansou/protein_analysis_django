from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'protein_analysis_tool/index.html'
