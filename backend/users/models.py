from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

MAX_LENGTH = 150
MAX_LENGTH_EMAIL = 254


class User(AbstractUser):
    '''Измененная модель пользователя.'''

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username",)

    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
    )
    username = models.CharField(
        max_length=MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Не допускаются: пробел и символы, кроме . @ + - _',
            ),
        ]
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH,
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    '''Модель подписки на автора.'''
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    following = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'following')
