from typing import List

from django import forms
from django.core import exceptions
from django.db.models.base import Model
from django.db.models.query import QuerySet


class MultipleObjectCSVField(forms.Field):
    """Custom field to specify multiple objects (comma-separated)."""

    def __init__(self, queryset: QuerySet, to_field_name: str, **kwargs):
        """Check if to_field is valid while initializing."""
        try:
            queryset.model._meta.get_field(to_field_name)
        except AttributeError as e:
            raise ValueError(
                'Invalid queryset for {}'.format(self.__class__.__name__)
            ) from e
        except exceptions.FieldDoesNotExist as e:
            raise ValueError(
                'Field \'{}\' does not exist in the specified queryset'.format(to_field_name)
            ) from e
        self.queryset = queryset
        self.to_field_name = to_field_name
        super().__init__(**kwargs)

    def clean(self, value) -> List[Model]:
        """Split the CSV and return a list of referenced objects."""
        if value in self.empty_values:
            if self.required:
                raise exceptions.ValidationError(self.error_messages['required'], code='required')
            else:
                return []

        lookup_values = [val.strip() for val in value.split(',')]
        objects: List[Model] = []
        for val in lookup_values:
            try:
                obj = self.queryset.get(**{self.to_field_name: val})
            except self.queryset.model.DoesNotExist as e:
                raise exceptions.ValidationError(
                    'Object identified by the value \'{}\' does not exist'.format(val),
                    code='nonexistent_object',
                ) from e
            except exceptions.MultipleObjectsReturned:
                raise exceptions.ValidationError(
                    'Multiple objects identified by the value \'{}\''.format(val),
                    code='too_many_objects',
                )
            objects.append(obj)
        return objects
