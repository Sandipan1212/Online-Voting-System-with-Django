# from celery import shared_task
# from django.core.mail import send_mail

# @shared_task
# def send_vote_confirmation_email(user_email, topic_title, selected_option):
#     """Send an email to the user confirming their vote."""
#     subject = "Vote Confirmation"
#     message = f"Dear Voter,\n\nYou have successfully voted for '{selected_option}' in the topic '{topic_title}'.\n\nThank you for participating!"
#     from_email = 'sandipanmajumdar1234@gmail.com'  # Replace with your email
#     recipient_list = [user_email]

#     send_mail(subject, message, from_email, recipient_list)
#     return f"Email sent to {user_email}"




from celery import shared_task

@shared_task
def test_task():
    print("✅ Celery task executed successfully!")
    return "Task completed"