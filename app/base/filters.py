from admin_auto_filters.filters import AutocompleteFilter
from django.db.models import ManyToOneRel, ManyToManyRel
from django.db.models.fields.related_descriptors import (
    ReverseManyToOneDescriptor, ManyToManyDescriptor)



class BaseAutocompleteFilter(AutocompleteFilter):
    nested_model = None

    def __init__(self, request, params, model, model_admin):
        model = self.nested_model or model
        super().__init__(request, params, model, model_admin)

    @staticmethod
    def get_queryset_for_field(model, name):
        try:
            field_desc = getattr(model, name)
        except AttributeError:
            field_desc = model._meta.get_field(name)
        if isinstance(field_desc, ManyToManyDescriptor):
            related_model = field_desc.rel.related_model if field_desc.reverse else field_desc.rel.model
        elif isinstance(field_desc, ReverseManyToOneDescriptor):
            related_model = field_desc.rel.related_model  # look at field_desc.related_manager_cls()?
        elif isinstance(field_desc, (ManyToOneRel, ManyToManyRel)):
            related_model = field_desc.related_model
        else:
            return field_desc.get_queryset()
        return related_model.objects.get_queryset()    
