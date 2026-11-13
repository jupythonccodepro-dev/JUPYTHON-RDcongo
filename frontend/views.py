from django.shortcuts import render
from django.views.generic import TemplateView


class FrontendPageView(TemplateView):
    """Simple fallback view used to render frontend HTML pages."""

    def get_template_names(self):
        template_name = self.kwargs.get('template_name', 'index.html')
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_CLIENT_ID'] = self.request.GET.get('google_client_id', '')
        return context


def home_view(request):
    return render(request, 'index.html', {'GOOGLE_CLIENT_ID': ''})
