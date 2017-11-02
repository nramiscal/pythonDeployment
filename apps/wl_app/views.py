from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from models import User, UserManager, Wish, WishManager, Join, Message, Comment, MessageManager, CommentManager
from datetime import datetime
# from time import localtime, strftime, gmtime
import bcrypt


def index(request):
    # User.objects.all().delete()
    # Wish.objects.all().delete()
    # Join.objects.all().delete()
    return render(request, 'wl_app/index.html')


def register(request):
    val = User.objects.regValidator(request.POST)

    if val[0]:
        request.session['name'] = val[1].name
        request.session['id'] = val[1].id

        return redirect('/my_page')
    else:
        for error in val[1]:
            messages.add_message(request, messages.ERROR, error)
        return redirect('/')


def login(request):
    val = User.objects.loginValidator(request.POST)

    if val[0]:
        request.session['id'] = val[1].id
        request.session['name'] = val[1].name
        return redirect('/wall')
    else:
        for error in val[1]:
            messages.add_message(request, messages.ERROR, error)
        return redirect('/')

def wall(request):
    messages = Message.objects.order_by("-created_at")
    comments = Comment.objects.all()
    # now = strftime("%a, %d %b %Y %H:%M", gmtime())
    return render(request, 'wl_app/wall.html', {"messages": messages, "comments": comments})

def createMessage(request):
    val = Message.objects.msgValidator(request.POST['message'], request.session['id'])

    if val[0]:
        return redirect('/wall')
    else:
        for error in val[1]:
            messages.add_message(request, messages.ERROR, error)
        return redirect('/wall')

def createComment(request):
    val = Comment.objects.commentValidator(request.POST['comment'], request.session['id'], request.POST['message_id'])

    if val[0]:
        return redirect('/wall')
    else:
        for error in val[1]:
            messages.add_message(request, messages.ERROR, error)
        return redirect('/wall')


def my_page(request):
    #all wishes this user has
    wishes = Wish.objects.all()

    joins = Join.objects.filter(user_id=request.session['id'])

    #remove wishes that also are in joins
    for join in joins:
        wishes = wishes.exclude(id = join.wish_id)

    return render(request, 'wl_app/my_page.html', {"wishes" : wishes, "joins" : joins})


def add(request):
    return render(request, 'wl_app/create.html')


def create(request):

    val = Wish.objects.wishValidator(request.POST['item'], request.session['id'])
    if val[0]:
        return redirect('/my_page')
    else:
        for error in val[1]:
            messages.add_message(request, messages.ERROR, error)
        return render(request, 'wl_app/create.html')


def logout(request):
    request.session.clear()
    return redirect('/')


def home(request):
    return redirect('/my_page')


def join(request, wish_id):
    user = User.objects.get(id=request.session['id'])
    wish = Wish.objects.get(id = wish_id)

    Join.objects.create(user_id=request.session['id'], wish_id=wish_id)
    return redirect('/my_page')


def delete(request, wish_id):
    Wish.objects.get(id = wish_id).delete()
    return redirect('/my_page')

def deleteMessage(request, message_id):

    # timeCreated = Message.objects.get(id=message_id).created_at
    # now = timezone.now()
    # diff = now - timeCreated

    Message.objects.get(id = message_id).delete()
    return redirect('/wall')


def remove(request, wish_id):
    Join.objects.filter(user_id = request.session['id']).get(wish_id = wish_id).delete()
    return redirect('/my_page')


def wish_item(request, wish_id):
    wish = Wish.objects.get(id=wish_id)
    wisher = User.objects.get(id = wish.wisher_id)
    joins = Join.objects.filter(wish_id = wish_id)

    data = {
        "wish" : wish,
        "wisher" : wisher,
        "joins" : joins,
    }

    return render(request, 'wl_app/item.html', data)
