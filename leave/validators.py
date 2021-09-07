import mimetypes


def validate_file_extension(value):
    from django.core.exceptions import ValidationError
    types = mimetypes.guess_type(value.name)[0]
    valid_types = ['application/pdf', 'application/msword',
                   'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg',
                   'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                   'application/vnd.ms-excel']
    if types not in valid_types:
        raise ValidationError(u'Unsupported file extension.')

    limit = 5 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 5MB.')
