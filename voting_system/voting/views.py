from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import VotingTopic, VotingOption, Vote
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm

from .forms import SignUpForm

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')  
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

           
            if user.role == 'admin':
                return redirect('admin_dashboard')  
            elif user.role == 'voter':
                return redirect('voter_dashboard')  
            else:
                return redirect('home') 
        else:
            return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials'})

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  


def admin_dashboard(request):
    
    if request.user.role != 'admin':
        return redirect('home')

    
    topics = VotingTopic.objects.all()

   
    return render(request, 'admin_dashboard.html', {'topics': topics})


from .models import VotingTopic, VotingOption
from .forms import VotingTopicForm, VotingOptionForm
@login_required
def create_voting_topic(request):
    if request.user.role != 'admin':
        return redirect('home')  
    
    if request.method == 'POST':
        form = VotingTopicForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')  
    else:
        form = VotingTopicForm()

    return render(request, 'create_voting_topic.html', {'form': form})









from django.shortcuts import render, redirect, get_object_or_404
from .models import VotingTopic, VotingOption
from .forms import VotingOptionForm
from django.contrib.auth.decorators import login_required

@login_required
def create_voting_option(request, topic_id):
    if request.user.role != 'admin':
        return redirect('home')  

    topic = get_object_or_404(VotingTopic, id=topic_id)

    if request.method == 'POST':
        form = VotingOptionForm(request.POST)
        if form.is_valid():
            option = form.save(commit=False)
            option.topic = topic  
            option.save()  
            return redirect('admin_dashboard')  
    else:
        form = VotingOptionForm()

    return render(request, 'create_voting_option.html', {'form': form, 'topic': topic})


def home(request):
    return render(request, 'home.html')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import VotingTopic, Vote, VotingOption

@login_required
def voter_dashboard(request):
    
    if request.user.role != 'voter':
        return redirect('home')  

   
    current_time = timezone.now()

  
    active_topics = VotingTopic.objects.filter(start_time__lte=current_time, end_time__gte=current_time).prefetch_related('options')


    
    if not active_topics:
        return render(request, 'voter_dashboard.html', {'message': 'No active voting topics available.'})

    
    for topic in active_topics:
     
        print(f"Topic: {topic.title}, Options: {[option.option_text for option in topic.options.all()]}")  # Print the options for debugging

        if Vote.objects.filter(user=request.user, topic=topic).exists():
            topic.has_voted = True
        else:
            topic.has_voted = False
            
    for topic in active_topics:
        print(f"Topic: {topic.title}, Options: {topic.options.all()}")

    return render(request, 'voter_dashboard.html', {'topics': active_topics})




from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import VotingTopic, VotingOption, Vote
from .rabbitmq import get_rabbitmq_connection
import json
import pika
from .tasks import process_vote, send_vote_confirmation_email
@login_required
@user_passes_test(lambda u: u.role == 'voter')  
def vote_topic(request, topic_id):
    print("🟢 Entered vote_topic function")

    topic = get_object_or_404(VotingTopic, id=topic_id)

    # Check if voting is open
    if timezone.now() < topic.start_time or timezone.now() > topic.end_time:
        print("❌ Voting is not active.")
        return render(request, 'vote_topic.html', {'topic': topic, 'options': topic.options.all(), 'error': 'Voting is not allowed outside the active period.'})

    # Check if user has already voted
    if Vote.objects.filter(user=request.user, topic=topic).exists():
        print("⚠️ User has already voted.")
        return redirect('results', topic_id=topic.id)

    if request.method == 'POST':
        print("🟢 Received POST request for voting")

        selected_option_id = request.POST.get('vote')
        if not selected_option_id:
            print("❌ No option selected.")
            return render(request, 'vote_topic.html', {'topic': topic, 'options': topic.options.all(), 'error': 'You must select an option to vote.'})

        selected_option = get_object_or_404(VotingOption, id=selected_option_id)

        # Save the vote in the database
        vote = Vote.objects.create(user=request.user, topic=topic, selected_option=selected_option)
        print(f"✅ Vote saved: {request.user.username} -> {selected_option.option_text}")

        # Try to send a message to RabbitMQ
        try:
            print("🔄 Connecting to RabbitMQ...")
            connection, channel = get_rabbitmq_connection()
            print("✅ Connected to RabbitMQ.")

            # Ensure the queue is declared properly
            channel.queue_declare(queue='vote_queue', durable=True)

            message = json.dumps({
                "username": request.user.username,
                "topic_title": topic.title,
                "option_text": selected_option.option_text
            })
            print(f"📨 Sending message: {message}")

            # Publish the message
            channel.basic_publish(
                exchange='',
                routing_key='vote_queue',
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)  # Make the message persistent
            )

            print("✅ Message sent to RabbitMQ!")
            connection.close()
        
        except Exception as e:
            print(f"❌ Error sending message to RabbitMQ: {e}")
            
            
         # Call Celery Tasks Asynchronously
        process_vote.delay({
            "username": request.user.username,
            "topic_title": topic.title,
            "option_text": selected_option.option_text
        })

        send_vote_confirmation_email.delay(request.user.email, topic.title, selected_option.option_text)
        print("mail sent")

        
        return redirect('results', topic_id=topic.id)

    options = topic.options.all()
    return render(request, 'vote_topic.html', {'topic': topic, 'options': options})











from django.shortcuts import render, get_object_or_404
from .models import VotingTopic, VotingOption, Vote

def results_view(request, topic_id):
    topic = get_object_or_404(VotingTopic, id=topic_id)
    options = VotingOption.objects.filter(topic=topic)

    results = []
    for option in options:
        count = Vote.objects.filter(selected_option=option).count()
        results.append({'option_text': option.option_text, 'votes': count})
        print(f"Option: {option.option_text}, Votes: {count}")

    is_admin = request.user.role == 'admin'
    user_voted = Vote.objects.filter(user=request.user, topic=topic).exists()

    return render(request, 'results.html', {
        'topic': topic,
        'results': results,
        'is_admin': is_admin,
        'user_voted': user_voted ,
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import VotingTopic, VotingOption
from django.http import Http404


def is_admin(user):
    return user.role == 'admin'


@login_required
@user_passes_test(is_admin)
def delete_voting_topic(request, topic_id):
    topic = get_object_or_404(VotingTopic, id=topic_id)
    topic.delete()  
    return redirect('admin_dashboard')  

@login_required
@user_passes_test(is_admin)
def delete_voting_option(request, option_id):
    option = get_object_or_404(VotingOption, id=option_id)
    topic_id = option.topic.id  
    option.delete()  
    return redirect('results', topic_id=topic_id)  


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import VotingTopic, VotingOption, Vote
from .serializers import VotingTopicSerializer, VotingOptionSerializer, VoteSerializer
from .forms import SignUpForm, VotingTopicForm, VotingOptionForm



class VotingTopicListCreateAPIView(APIView):
    def get(self, request):
        cache_key = "voting_topics"
        cached_topics = cache.get(cache_key)
        if cached_topics:
            print("Data from REDIS")
            print(cached_topics)
            return Response(cached_topics)
        print("Data from POSTGRES")
        topics = VotingTopic.objects.all()
        serializer = VotingTopicSerializer(topics, many=True)
        cache.set(cache_key, serializer.data, timeout=3600)  # Store for 1 hour
        return Response(serializer.data)

    def post(self, request):
        serializer = VotingTopicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete("voting_topics")  # Clear cache after modification
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VotingTopicRetrieveUpdateDestroyAPIView(APIView):
    def get(self, request, topic_id):
        try:
            topic = VotingTopic.objects.get(id=topic_id)
            serializer = VotingTopicSerializer(topic)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except VotingTopic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, topic_id):
        """Delete a topic and store it in Redis"""
        try:
            topic = VotingTopic.objects.get(id=topic_id)
            serializer = VotingTopicSerializer(topic)

            # Store deleted topic in Redis for 1 hour (3600 seconds)
            cache_key = f"deleted_topic_{topic_id}"
            cache.set(cache_key, serializer.data, timeout=3600)

            print(f"Deleted topic stored in Redis: {cache.get(cache_key)}")  # Debugging

            topic.delete()
            return Response({"message": "Topic deleted and stored in cache."}, status=status.HTTP_200_OK)
        except VotingTopic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)

from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import VotingTopic
from .serializers import VotingTopicSerializer

class VotingTopicRestoreAPIView(APIView):
    def post(self, request, topic_id):
        """Restore a deleted topic from Redis"""
        cache_key = f"deleted_topic_{topic_id}"
        deleted_topic_data = cache.get(cache_key)

        if not deleted_topic_data:
            return Response({"error": "No deleted topic found in cache."}, status=status.HTTP_404_NOT_FOUND)

        print(f"Found deleted topic in Redis: {deleted_topic_data}")  # Debugging

        # Deserialize and restore the topic
        serializer = VotingTopicSerializer(data=deleted_topic_data)
        if serializer.is_valid():
            serializer.save()

            # Remove from cache after restoring
            cache.delete(cache_key)
            return Response({"message": "Topic restored successfully."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class VotingOptionAPIView(APIView):
    def get(self, request, topic_id):
        options = VotingOption.objects.filter(topic_id=topic_id)
        serializer = VotingOptionSerializer(options, many=True)
        return Response(serializer.data)

    def post(self, request, topic_id):
        data = request.data
        data['topic'] = topic_id  
        serializer = VotingOptionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VoteView(APIView):
    def post(self, request):
        serializer = VoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
from django.core.cache import cache

def print_redis_data(request):
    # Define the cache key you want to retrieve
    cache_key = "voting_topics"

    # Retrieve data from Redis using the cache key
    cached_data = cache.get(cache_key)

    if cached_data:
        print("Data from Redis:", cached_data)
        return render(request, 'redis_data.html', {'data': cached_data})
    else:
        print("No data found in Redis for key:", cache_key)
        return render(request, 'redis_data.html', {'message': 'No data found in Redis.'})