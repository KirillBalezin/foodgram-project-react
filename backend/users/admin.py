from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from users.models import User, Follow


class CustomUserAdmin(UserAdmin):
    '''Настройки админки для модели User.'''
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')
    ordering = ('pk',)


class SubscriptionAdmin(admin.ModelAdmin):
    '''Настройки админки для модели Subscription.'''
    list_display = ('user', 'following')
    search_fields = ('user__username', 'following__username')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow, SubscriptionAdmin)
admin.site.unregister(Group)
