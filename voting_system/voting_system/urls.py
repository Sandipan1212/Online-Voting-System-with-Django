"""
URL configuration for voting_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from voting import views
from voting.views import VotingTopicListCreateAPIView, VotingOptionAPIView, VoteView
from voting.views import VotingTopicRetrieveUpdateDestroyAPIView, VotingTopicRestoreAPIView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('voter_dashboard/', views.voter_dashboard, name='voter_dashboard'),
    path('create_voting_topic/', views.create_voting_topic, name='create_voting_topic'),
    path('create_voting_option/<int:topic_id>/', views.create_voting_option, name='create_voting_option'),
    path('vote/<int:topic_id>/', views.vote_topic, name='vote'),
    path('results/<int:topic_id>/', views.results_view, name='results'),
    path('topic/<int:topic_id>/delete/', views.delete_voting_topic, name='delete_voting_topic'),
    path('option/<int:option_id>/delete/', views.delete_voting_option, name='delete_voting_option'),
    path('api/topics/', VotingTopicListCreateAPIView.as_view(), name='api_topics'),
    path('api/topics/<int:topic_id>/', VotingTopicRetrieveUpdateDestroyAPIView.as_view(), name='topic-detail'),
    path('api/topics/<int:topic_id>/options/', VotingOptionAPIView.as_view(), name='api_options'),
    path('api/vote/', VoteView.as_view(), name='api_vote'),
    path('api/topics/<int:topic_id>/', VotingTopicRetrieveUpdateDestroyAPIView.as_view(), name='topic-delete'),
    path('api/topics/<int:topic_id>/restore/', VotingTopicRestoreAPIView.as_view(), name='topic-restore'),
    path('print-redis-data/', views.print_redis_data, name='print_redis_data'),

]
