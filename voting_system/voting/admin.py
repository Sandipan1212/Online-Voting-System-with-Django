from django.contrib import admin
from .models import VotingTopic, VotingOption, Vote, CustomUser

# admin.site.register(VotingTopic)
admin.site.register(VotingOption)
admin.site.register(Vote)
admin.site.register(CustomUser)



# Register the VotingTopic model
class VotingTopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_time', 'end_time', 'description']  
    search_fields = ['title', 'description']  


class VotingOptionAdmin(admin.ModelAdmin):
    list_display = ['topic', 'option_text']  
    search_fields = ['option_text']  


admin.site.register(VotingTopic, VotingTopicAdmin)



# # Admin (Optional)
# # from django.contrib import admin
# # from .models import VotingTopic

# @admin.register(VotingTopic)
# class VotingTopicAdmin(admin.ModelAdmin):
#     list_display = ('title', 'start_time', 'end_time')
