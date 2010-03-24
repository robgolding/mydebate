## 
## Author: Rob Golding
## Project: myDebate
## Group: gp09-sdb
## 

from django.contrib import admin

from models import Room, Message, Membership

admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Membership)
