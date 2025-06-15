from django.contrib import admin
from .models import Message, MessageHistory

class MessageHistoryInline(admin.TabularInline):
    model = MessageHistory
    extra = 0
    readonly_fields = ('edit_timestamp', 'edited_by', 'old_content')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'last_edited', 'edited', 'is_read')
    list_filter = ('sender', 'receiver', 'edited', 'is_read')
    search_fields = ('content',)
    readonly_fields = ('timestamp', 'last_edited', 'edited')
    inlines = [MessageHistoryInline]
    
    fieldsets = (
        (None, {'fields': ('sender', 'receiver')}),
        ('Content', {'fields': ('content',)}),
        ('Status', {'fields': ('is_read',)}),
        ('Metadata', {'fields': ('timestamp', 'last_edited', 'edited')}),
    )

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'edit_timestamp', 'edited_by', 'content_preview')
    list_filter = ('edit_timestamp', 'edited_by')
    search_fields = ('old_content', 'message__content')
    readonly_fields = ('message', 'old_content', 'edit_timestamp', 'edited_by')
    
    def has_add_permission(self, request):
        return False
    
    def content_preview(self, obj):
        return obj.old_content[:50] + '...' if len(obj.old_content) > 50 else obj.old_content
    content_preview.short_description = 'Content Preview'
