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
    list_display = ('sender', 'receiver', 'timestamp', 'last_edited', 'edited')
    list_filter = ('sender', 'receiver', 'edited')
    search_fields = ('content',)
    readonly_fields = ('timestamp', 'last_edited', 'edited')
    inlines = [MessageHistoryInline]
    
    fieldsets = (
        (None, {'fields': ('sender', 'receiver')}),
        ('Content', {'fields': ('content',)}),
        ('Metadata', {'fields': ('timestamp', 'last_edited', 'edited')}),
    )

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'edit_timestamp', 'edited_by')
    list_filter = ('edit_timestamp', 'edited_by')
    search_fields = ('old_content',)
    readonly_fields = ('message', 'old_content', 'edit_timestamp', 'edited_by')
    
    def has_add_permission(self, request):
        return False
