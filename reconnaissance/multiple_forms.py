from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import ProcessFormView


class MultipleFormsMixin(ContextMixin):
    """
    A mixin that provides a way to show and handle multiple forms in a request.
    It's almost fully-compatible with regular FormsMixin
    """

    initial = {}
    forms_classes = []
    success_url = None
    prefix = None
    active_form_keyword = "selected_form"

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        return self.initial.copy()

    def get_prefix(self):
        """
        Returns the prefix to use for forms on this view
        """
        return self.prefix

    def get_forms_classes(self):
        """
        Returns the forms classes to use in this view. Can be dynamic.
        """
        return self.forms_classes

    def get_active_form_number(self):
        """
        Returns submitted form index in available forms list
        """
        if self.request.method in ('POST', 'PUT'):
            try:
                return int(self.request.POST[self.active_form_keyword])
            except (KeyError, ValueError):
                raise ImproperlyConfigured(
                    "You must include hidden field with field index in every form! Example:")

    def get_forms(self, active_form=None):
        """
        Returns instances of the forms to be used in this view.
        Includes provided `active_form` in forms list.
        """
        all_forms_classes = self.get_forms_classes()
        all_forms = [
            form_class(**self.get_form_kwargs()) 
            for form_class in all_forms_classes]
        if active_form:
            active_form_number = self.get_active_form_number()
            all_forms[active_form_number] = active_form
        return all_forms

    def get_form(self):
        """
        Returns active form. Works only on `POST` and `PUT`, otherwise returns None.
        """
        active_form_number = self.get_active_form_number()
        if active_form_number is not None:            
            all_forms_classes = self.get_forms_classes()
            active_form_class = all_forms_classes[active_form_number]
            return active_form_class(**self.get_form_kwargs(is_active=True))

    def get_form_kwargs(self, is_active=False):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if is_active:
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_success_url(self):
        """
        Returns the supplied success URL.
        """
        if self.success_url:
            # Forcing possible reverse_lazy evaluation
            url = force_text(self.success_url)
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(self.get_context_data(active_form=form))

    def get_context_data(self, **kwargs):
        """
        Insert the forms into the context dict.
        """
        if 'forms' not in kwargs:
            kwargs['forms'] = self.get_forms(kwargs.get('active_form'))
        return super(MultipleFormsMixin, self).get_context_data(**kwargs)

      
class MultipleFormsView(TemplateResponseMixin, MultipleFormsMixin, ProcessFormView):
    pass