from django.contrib import admin

# Register your models here.
from membership.models import Customer

admin.site.register(Customer)