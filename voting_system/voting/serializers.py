from rest_framework import serializers
from .models import VotingTopic, VotingOption, Vote

class VotingTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = VotingTopic
        fields = '__all__'

class VotingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VotingOption
        fields = '__all__'

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'
