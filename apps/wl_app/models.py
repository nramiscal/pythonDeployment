from __future__ import unicode_literals
from django.db import models
from datetime import datetime
import bcrypt
import re
# re = regex

now = datetime.now()

class MessageManager(models.Manager):
    def msgValidator(self, message, id):
        errors = []

        if len(message) < 1:
            errors.append("Please input a message.")


        if len(errors) > 0:
            return (False, errors)
        else:
            message = Message.objects.create(message = message, author_id=id)
            return (True, message)


class CommentManager(models.Manager):
    def commentValidator(self, comment, author_id, message_id):
        errors = []

        if len(comment) < 1:
            errors.append("Please input a comment.")


        if len(errors) > 0:
            return (False, errors)
        else:
            comment = Comment.objects.create(comment = comment, author_id=author_id, message_id=message_id)
            return (True, comment)


class WishManager(models.Manager):
    def wishValidator(self, item, id):
        errors = []

        if len(item) < 3:
            errors.append("Item name must be at least 3 characters.")

        if len(errors) > 0:
            return (False, errors)

        else:
            wish = Wish.objects.create(item = item, wisher_id = id)
            Join.objects.create(user_id=id, wish_id=wish.id)
            return (True, wish)


class UserManager(models.Manager):
    def regValidator(self, form):
        errors = []

        if len(form['name']) < 3:
            errors.append("Name must be at least 3 characters.")
        elif not re.match('[A-Za-z]+', form['name']):
            errors.append("Name must only contain letters.")

        if len(form['username']) < 3:
            errors.append("Username must be at least 3 characters.")
        elif User.objects.filter(username=form['username']):
            errors.append("Username is taken.")

        if len(form['password']) < 8:
            errors.append("Password must be at least 8 characters.")

        if len(form['confirm_pw']) < 1:
            errors.append("Password confirmation is required.")
        if form['password'] != form['confirm_pw']:
            errors.append("Passwords do not match.")

        if len(form['date_hired']) < 1:
            errors.append("Date hired is required.")
        elif datetime.strptime(form['date_hired'], '%Y-%m-%d') > now:
            errors.append("Invalid hired date. Date cannot be in the future.")

        if len(errors) > 0:
            return (False, errors)
        else:
            pwhash = bcrypt.hashpw(form['password'].encode(), bcrypt.gensalt())

            user = User.objects.create(name = form['name'], username = form['username'], password = pwhash, date_hired = form['date_hired'])
            return (True, user)


    def loginValidator(self, form):
        errors = []
        username = form['username']
        password = form['password']

        if len(username) < 1:
            errors.append("Please input a username.")
        elif not User.objects.filter(username=username):
            errors.append("This username is not registered in our database.")

        if len(password) < 1:
            errors.append("Please input a password.")

        if User.objects.filter(username=username):
            user = User.objects.get(username = username)
            if not bcrypt.hashpw(str(password), str(user.password)) == user.password:
                errors.append("Incorrect password: does not match password stored in database.")

        if len(errors) > 0:
            return (False, errors)
        else:
            user = User.objects.get(username = username)
            return (True, user)


class User(models.Model):
    name = models.CharField(max_length = 255)
    username = models.CharField(max_length = 255)
    password = models.CharField(max_length = 255)
    date_hired = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = UserManager()
    def __repr__(self):
        return "<UserObject: {} {} {}>".format(self.id, self.name, self.username)

class Wish(models.Model):
    item = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    wisher = models.ForeignKey(User, related_name = "wishes")
    objects = WishManager()
    def __repr__(self):
        return "<WishObject: {}>".format(self.item)

class Join(models.Model):
    user = models.ForeignKey(User, related_name = "users")
    wish = models.ForeignKey(Wish, related_name = "wishes")
    def __repr__(self):
        return "<JoinObject: User_id = {} Wish_id = {}>".format(self.user_id, self.wish_id)

# adding Message and Comment tables
# Comment is the join table of User and Message

class Message(models.Model):
    message = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    author = models.ForeignKey(User, related_name = "messages")
    objects = MessageManager()
    def __repr__(self):
        return "<MessageObject: {} {} {}>".format(self.message, self.author, self.created_at)

class Comment(models.Model):
    comment = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    author = models.ForeignKey(User, related_name = "authors")
    message = models.ForeignKey(Message, related_name = "messages")
    objects = CommentManager()
    def __repr__(self):
        return "<CommentObject: {} User_id = {} Message_id = {} {}>".format(self.comment, self.author_id, self.message_id, self.created_at)
