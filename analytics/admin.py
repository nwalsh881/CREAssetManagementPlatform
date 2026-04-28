from django.contrib import admin

# Register your models here.
from .models import Market, Submarket, PropertyType, Property, Lease

admin.site.register(Market)
admin.site.register(Submarket)
admin.site.register(PropertyType)
admin.site.register(Property)
admin.site.register(Lease)