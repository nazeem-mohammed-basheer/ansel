# bodhini_project/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView # <--- IMPORTANT CHANGE: Import TemplateView

# Change View to TemplateView
class AuthenticatedTemplateView(LoginRequiredMixin, TemplateView): # <--- IMPORTANT CHANGE: Inherit from TemplateView
    # The template_name attribute is now automatically handled by TemplateView.
    # You don't need a custom get method unless you have additional context or logic.

    # You can remove the get method if you only need to render a template and require login.
    # If you need to add custom context or logic, you would use get_context_data or override get.
    # For now, let's keep a simplified get method to show the debug print,
    # but technically TemplateView will handle the rendering without it.

    def get(self, request, *args, **kwargs):
        # self.template_name is now guaranteed to be set by TemplateView's as_view
        print(f"--- DEBUG: User authenticated. Rendering {self.template_name} ---")
        return super().get(request, *args, **kwargs) # Call the parent TemplateView's get method
                                                     # which handles rendering the template.

    # If you need to pass extra context to your templates, you'd use get_context_data:
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['my_custom_data'] = 'Some value'
    #     return context