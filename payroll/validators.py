from django.core.exceptions import ValidationError


def validate_file_size(value):
    filesize = value.size

    if filesize > 2000000:
        raise ValidationError('The maximum file size for a file is 2 MB')

    return value
