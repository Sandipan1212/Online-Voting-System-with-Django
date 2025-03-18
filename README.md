This is a Django-based voting system where users can sign up, log in, vote on topics, and view the
results. Admins can create and manage voting topics and options, while voters can cast their votes
on active topics.

KEY LIBRARIES/TOOLS USED
• Django: The main framework for building the application.
• Redis: Used for caching voting topics and storing deleted topics.
• Celery: Used for asynchronous task processing (e.g., sending confirmation emails).
• RabbitMQ: Used for messaging to handle vote processing tasks.
• Django REST Framework: Used to create API views for voting topics, options, and votes.
• pika: Used to connect to RabbitMQ and send messages.
• Gunicorn: A WSGI HTTP server for running the Django application in production, ensuring that
requests are handled efficiently and securely.
• Nginx: A high-performance web server used for serving static files, acting as a reverse proxy for
Gunicorn, and enabling HTTPS.
