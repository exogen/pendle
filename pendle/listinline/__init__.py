from django import forms
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.forms.models import BaseInlineFormSet
from django.forms.models import _get_foreign_key
from django.utils.translation import ugettext as _
from django.conf.urls.defaults import patterns, url


REMOVAL_FIELD_NAME = 'REMOVE'

class ListInlineModelAdmin(admin.ModelAdmin):
    def get_urls(self):
        urlpatterns = super(ListInlineModelAdmin, self).urls
        for inline in self.inline_instances:
            urlpatterns += inline.urls
        return urlpatterns

    urls = property(get_urls)

class SearchForm(forms.Form):
    QUERY = forms.CharField(label="Search", required=False,
                            widget=forms.TextInput(attrs={'class': 'search',
                                                          'size': 40}))


class ListInlineFormset(BaseInlineFormSet):
    can_remove = False

    def search_form(self):
        return SearchForm(prefix=self.prefix)

    def add_fields(self, form, index):
        super(ListInlineFormset, self).add_fields(form, index)
        if self.can_remove:
            label = _(u"Remove from %s" % self.fk.verbose_name)
            removal_field = forms.BooleanField(label=label, required=False)
            form.fields[REMOVAL_FIELD_NAME] = removal_field

    def save_existing(self, form, instance, commit=True):
        if self.can_remove and form.cleaned_data[REMOVAL_FIELD_NAME]:
            setattr(instance, self.fk.name, None)
        return super(ListInlineFormset, self).save_existing(form, instance, commit)


class ListInline(InlineModelAdmin):
    template = "listinline/list.html"
    formset = ListInlineFormset
    can_remove = False
    show_labels = True
    media = forms.Media(css={'all': ['listinline/css/list-inline.css']},
                        js=['js/jquery-1.5.1.min.js',
                            'js/jquery-ui-1.8.12.custom.min.js',
                            'listinline/js/sortable-inline.js'])

    def queryset(self, request):
        queryset = super(ListInline, self).queryset(request)
        if self.ordering:
            queryset = queryset.order_by(*self.ordering)
        return queryset

    def get_formset(self, *args, **kwargs):
        formset = super(ListInline, self).get_formset(*args, **kwargs)
        formset.can_remove = self.can_remove
        return formset

    def get_urls(self):
        return patterns('', 
            url(r'^(.+)/search/%s/$' % self.fk_name,
                self.admin_site.admin_view(self.search_view),
                name='search'))

    def search_view(self, request):
        pass

