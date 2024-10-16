from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.core.exceptions import ObjectDoesNotExist

from .models import Author, Story

from datetime import datetime, date
import json

# login request
@csrf_exempt
def handleLogin(request):
    if(request.method == 'POST'):
        # get username and password
        uname = request.POST.get('username')
        pword = request.POST.get('password')
        # make sure uname and pword are strings
        if not isinstance(uname, str) or not isinstance(pword, str):
            return HttpResponse("Username and password must be strings.", status=400, content_type='text/plain')
        # check user exists
        user = authenticate(request, username=uname, password=pword)
    else:
        # if not post, return appropriate error
        return HttpResponse("Method not allowed.", status=405, content_type='text/plain')
    # login if possible, return httpresponse to client
    if user is not None:
        login(request, user)
        return HttpResponse("You have logged in. Welcome!", status=200, reason='OK', content_type='text/plain')
    else:
        return HttpResponse("Invalid username or password. Please try again.", status=401, content_type='text/plain')
    

# logout request
@csrf_exempt
def handleLogout(request):
    if(request.method == 'POST'):
        if request.user.is_authenticated:
            logout(request)
            return HttpResponse("You have logged out. Goodbye.", status=200, reason='OK', content_type='text/plain')
        else:
            return HttpResponse("You are not logged in.", status=401, content_type='text/plain')
    else:
        # if not post, return appropriate error
        return HttpResponse("Method not allowed.", status=405, content_type='text/plain')


# stories request
@csrf_exempt
def stories(request):
    # if post -> author posting story
    if(request.method == 'POST'):
        # check if user is authenticated:
        if not request.user.is_authenticated:
            return HttpResponse("You are not logged in.", status=503, content_type='text/plain')
        
        # get body of json
        payload = json.loads(request.body)
        
        # check if category and region in correct form
        cats = ['pol', 'art', 'tech', 'trivia']
        regs = ['uk', 'eu', 'w']
        if payload.get('category') not in cats:
            return HttpResponse("Category should be: 'pol', 'art', 'tech' or 'trivia'.", status=503, reason='Service Unavailable', content_type='text/plain')
        if payload.get('region') not in regs:
            return HttpResponse("Region should be: 'uk', 'eu' or 'w'", status=503, reason='Service Unavailable', content_type='text/plain')
        
        # check that headline and details are not too long
        if len(payload.get('headline')) > 64 or len(payload.get('details')) > 128:
            return HttpResponse("Headline should be no more than 64 characters and Details should be no more than 128 characters", status=503, reason='Service Unavailable', content_type='text/plain')
        
        # if no errors, add story to db
        currentAuthor = Author.objects.get(user=request.user)
        currentDate = datetime.now().date()
        story = Story.objects.create(headline=payload.get('headline'), category=payload.get('category'), region=payload.get('region'), author=currentAuthor, date=currentDate, details=payload.get('details'))
        return HttpResponse(status=201, reason='CREATED')
    
    # if get -> user retrieving stories
    elif(request.method == 'GET'):
        cat = request.GET.get('story_cat')
        reg = request.GET.get('story_region')
        date = request.GET.get('story_date')

        # check if category, region and date in correct form
        cats = ['pol', 'art', 'tech', 'trivia', '*']
        regs = ['uk', 'eu', 'w', '*']
        if cat not in cats:
            return HttpResponse("Category should be: 'pol', 'art', 'tech' or 'trivia' if specifying.", status=400, content_type='text/plain')
        if reg not in regs:
            return HttpResponse("Region should be: 'uk', 'eu' or 'w' if specifying", status=400, content_type='text/plain')
        if date != '*':
            try:
                dateCheck = datetime.strptime(date, '%d/%m/%Y')
                if date != dateCheck.strftime('%d/%m/%Y'):
                    return HttpResponse("Date must be valid and in the format: 'dd/mm/YYYY'.", status=400, content_type='text/plain')
            except ValueError:
                    return HttpResponse("Date must be valid and in the format: 'dd/mm/YYYY'.", status=400, content_type='text/plain')
        
        # get all stories
        query = Story.objects.all()
        # get required category if needed
        if cat != '*':
            query = query.filter(category=cat)
        # get required region if needed
        if reg != '*':
            query = query.filter(region=reg)
        # get required dates if needed
        if date != '*':
            dateRequired = (datetime.strptime(date, "%d/%m/%Y")).date()
            query = query.filter(date__gte=dateRequired)

        # return error if no stories found
        if len(query) == 0 :
            return HttpResponse("No stories found", status=404, content_type="text/plain")
        else:
            # make queryset into list
            stories = query.values('id', 'headline', 'category', 'region', 'author', 'date', 'details')
            # format for json
            story_list = []
            for story in stories:
                storyAuthor = Author.objects.get(id=story['author'])
                authorName = storyAuthor.user.username
                item = {'key': str(story['id']), 'headline':story['headline'], 'story_cat':story['category'], 'story_region':story['region'], 'author': authorName, 'story_date':story['date'].strftime("%d/%m/%Y"), 'story_details': story['details']}
                story_list.append(item)
            # make payload
            payload = {'stories': story_list}
            return HttpResponse(json.dumps(payload), status=200, reason='OK', content_type='application/json')
    else:
        return HttpResponse("Method not allowed.", status=405, content_type='text/plain')
        

# delete request
@csrf_exempt
def delete(request, id):
    if(request.method == 'DELETE'):
        
        # check if user is authenticated:
        if not request.user.is_authenticated:
            return HttpResponse("You are not logged in.", status=503, reason='Service Unavailable', content_type='text/plain')

        # retrieve and delete story
        try:
            story = Story.objects.get(id=id)
            story.delete()
            return HttpResponse(status = 200, reason='OK')
        except ObjectDoesNotExist:
            return HttpResponse("Story does not exist.", status=503, reason='Service Unavailable', content_type='text/plain')

    else:
        return HttpResponse("Method not allowed.", status=503, reason='Service Unavailable', content_type='text/plain')