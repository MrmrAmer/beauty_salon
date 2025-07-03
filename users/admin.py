from django.contrib import admin
from .models import User, UserLevel

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'user_level', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_filter = ('user_level', 'created_at')

@admin.register(UserLevel)
class UserLevelAdmin(admin.ModelAdmin):
    list_display = ('level_name', 'created_at')
    search_fields = ('level_name',)