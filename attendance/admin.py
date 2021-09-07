from django.contrib import admin
from .models import model_list

for module in model_list:
    admin.site.register(module)
