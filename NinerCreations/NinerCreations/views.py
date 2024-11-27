# views.py
import re
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Post, Comment
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Post, Activity, Project
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.shortcuts import render, redirect
from django.contrib import messages
from .registerform import RegisterForm
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.core.exceptions import ValidationError
from .models import Profile
from .forms import ProfileForm
from .models import Post, Comment, Project, Profile
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Topic, Activity


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('-created_at')  # Fetch comments associated with the post

    if request.method == 'POST':
        content = request.POST.get('content')  # Get the comment content from the form

        if content:
            author = request.user if request.user.is_authenticated else None
            Comment.objects.create(post=post, author=author, content=content)
            # After adding the comment, fetch comments again to include the new one
            comments = post.comments.all().order_by('-created_at')

    # Render the post detail page with the post and comments
    return render(request, 'base/post_detail.html', {
        'post': post,
        'comments': comments,
    })
    
def recent_activity_view(request):
    # Query for the 10 most recent posts and comments
    recent_posts = Post.objects.all().order_by('-created_at')[:10]
    recent_comments = Comment.objects.all().order_by('-created_at')[:10]

    # Combine posts and comments into a single list and sort by created_at
    recent_activities = sorted(
        list(recent_posts) + list(recent_comments),
        key=lambda x: x.created_at,
        reverse=True
    )[:10]  # Get the top 10 most recent activities

    return render(request, 'base/home.html', {
        'recent_activities': recent_activities
    })

# views.py
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment, Topic


def home_view(request):
    topic_id = request.GET.get('topic')

    # Validate topic_id to ensure it's an integer
    if topic_id:
        try:
            topic_id = int(topic_id)
        except ValueError:
            # Pass the error_message context to the 400.html template
            return render(request, '400.html', {'error_message': 'Invalid topic parameter.'}, status=400)

    # Filter posts by topic if provided, otherwise return all posts
    if topic_id:
        posts = Post.objects.filter(topics__id=topic_id).order_by('-created_at')
        recent_posts = Post.objects.filter(topics__id=topic_id).order_by('-created_at')[:10]
    else:
        posts = Post.objects.all().order_by('-created_at')
        recent_posts = Post.objects.all().order_by('-created_at')[:10]

    # Retrieve comments related to the filtered posts
    post_ids = posts.values_list('id', flat=True)
    recent_comments = Comment.objects.filter(post__id__in=post_ids).order_by('-created_at')[:10]

    # Combine posts and comments, sorted by creation date, to get the 10 most recent activities
    recent_activities = sorted(
        list(recent_posts) + list(recent_comments),
        key=lambda x: x.created_at,
        reverse=True
    )[:10]

    # Retrieve all topics for the "Browse Topics" section
    topics = Topic.objects.all()

    # Pass the posts, recent activities, and topics to the template
    return render(request, 'base/home.html', {
        'posts': posts,
        'recent_activities': recent_activities,
        'topics': topics,
    })




@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    recent_rooms = Post.objects.filter(author=request.user).order_by('-created_at')[:5]
    recent_posts = Post.objects.filter(author=request.user).order_by('-created_at')[:10]
    recent_comments = Comment.objects.filter(author=request.user).order_by('-created_at')[:10]
    projects = Project.objects.filter(user=request.user)

    recent_activities = sorted(
        list(recent_posts) + list(recent_comments),
        key=lambda x: x.created_at,
        reverse=True
    )[:10]

    return render(request, 'base/profile.html', {
        'profile': profile,
        'recent_rooms': recent_rooms,
        'recent_activities': recent_activities,
        'projects': projects,
    })



def user_profile_view(request, pk):
    # Fetch the user object for the profile being viewed
    profile_user = get_object_or_404(User, pk=pk)
    profile, created = Profile.objects.get_or_create(user=profile_user)

    # Fetch recent rooms, posts, and comments by the profile owner
    recent_rooms = Post.objects.filter(author=profile_user).order_by('-created_at')[:5]
    recent_posts = Post.objects.filter(author=profile_user).order_by('-created_at')[:10]
    recent_comments = Comment.objects.filter(author=profile_user).order_by('-created_at')[:10]

    # Combine posts and comments, sorted by creation date
    recent_activities = sorted(
        list(recent_posts) + list(recent_comments),
        key=lambda x: x.created_at,
        reverse=True
    )[:10]

    # Fetch the completed projects for this profile owner
    projects = Project.objects.filter(user=profile_user).order_by('-created_at')

    # Include bio and profile picture in the context
    context = {
        'profile_user': profile_user,  # User whose profile is being viewed
        'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
        'bio': profile.bio or "This user has not added a bio yet.",
        'recent_rooms': recent_rooms,
        'recent_activities': recent_activities,
        'projects': projects,
    }
    return render(request, 'base/user_profile.html', context)




def create_post(request):
    if request.method == 'POST':
        # Handle post creation
        post = Post.objects.create(
            title=request.POST['title'],
            content=request.POST['content'],
            user=request.user
        )
        
        # Log the activity
        Activity.objects.create(user=request.user, action='CREATED_POST', post=post)
        
        # Redirect or render response
        return redirect('profile', pk=request.user.pk)
    
    return render(request, 'posts/create_post.html')
def search(request):
    query = request.GET.get('q', '')
    if query:
        # Search by title OR description using Q objects
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    else:
        posts = Post.objects.none()
    return render(request, 'base/search_results.html', {'posts': posts, 'query': query})

def home(request):
    return render(request, 'base/home.html')

def profile(request):
    return render(request, 'base/profile.html')

def settings(request):
    return render(request, 'base/settings.html')

def login(request):
    return render(request, 'base/login.html')

#Register account stuff
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)  # Include `request.FILES` for file upload
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please log in.')
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'base/register.html', {'form': form})
def handle_invalid_topic_id(request, exception):
    # Render the custom 400 error page
    return render(request, '400.html', status=400)

def is_valid_url(url):
    # General URL validation regex
    url_pattern = re.compile(
        r'^(https?:\/\/)?'  # http:// or https://
        r'([a-zA-Z0-9\-_]+\.)+[a-zA-Z]{2,}'  # Domain name
        r'(:\d+)?(\/.*)?$'  # Optional port and path
    )
    return bool(url_pattern.match(url))

def add_project(request):
    if request.method == 'POST':
        name = request.POST.get('project_name')
        description = request.POST.get('project_description')
        link = request.POST.get('project_link')

        # Validate URL
        if not is_valid_url(link):
            messages.error(request, "Please provide a valid URL.")
            return redirect('profile')  # Redirect back to profile with an error message

        # Save the project to the database
        Project.objects.create(user=request.user, name=name, description=description, github_link=link)
        messages.success(request, "Project added successfully!")
        return redirect('profile')

    return render(request, 'profile.html')

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Check if the project belongs to the logged-in user
    if project.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this project.")
    
    project.delete()
    return redirect('profile')  # Redirect back to the profile page

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Ensure only the owner can edit the project
    if project.user != request.user:
        return HttpResponseForbidden("You are not allowed to edit this project.")

    if request.method == 'POST':
        name = request.POST.get('project_name')
        description = request.POST.get('project_description')
        link = request.POST.get('project_link')

        # Validate URL
        if not is_valid_url(link):
            messages.error(request, "Please provide a valid URL.")
            return redirect('profile')  # Redirect back to profile with an error message

        # Update project details
        project.name = name
        project.description = description
        project.github_link = link
        project.save()

        messages.success(request, "Project updated successfully!")
        return redirect('profile')

    # Render an edit form if method is GET
    context = {'project': project}
    return render(request, 'base/edit_project.html', context)

# User Settings View
@login_required
def settings(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update ProfileForm for bio and profile picture
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        # Get new values for first name, last name, username, and email
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Get and validate password inputs
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if form.is_valid():
            # Update user details
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email

            # Handle password update if provided
            if password and password == confirm_password:
                user.set_password(password)

            # Save user and profile changes
            user.save()
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('settings')
        else:
            messages.error(request, "There was an error updating your profile.")

    else:
        form = ProfileForm(instance=profile)

    return render(request, 'base/settings.html', {
        'form': form,
        'profile': profile,
    })


# Delete Account View
@login_required
def delete_account(request):
    """
    View to handle account deletion for the logged-in user.
    """
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('home')

    return render(request, 'base/delete_account.html')

