from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.models import Token

class CustomUserAdmin(UserAdmin):
    actions = ['generate_tokens']

    def generate_tokens(self, request, queryset):
        for user in queryset:
            Token.objects.get_or_create(user=user)

    generate_tokens.short_description = "Generate tokens for selected users"

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
