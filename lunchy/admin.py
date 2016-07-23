# file used by the admin app
# register here models that can be changed with django admin

from django.contrib import admin

from .models import *

class PersonAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'bio', 'email')

class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('lunch_date', 'person_nickname')
    def person_nickname(self, obj):
        return obj.person.nickname

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('lunch_date', 'get_persons', 'place', 'detail', 'google_id')


admin.site.register(Person, PersonAdmin)
admin.site.register(Availability, AvailabilityAdmin)
admin.site.register(Appointment, AppointmentAdmin)