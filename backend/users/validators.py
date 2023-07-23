from django.core.exceptions import ValidationError


def validate_username_me(value):
    if value == 'me':
        raise ValidationError(
            'Имя пользователя не может быть: me'
        )
    return value
