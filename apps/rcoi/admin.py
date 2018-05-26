from django.contrib import admin

from . import models


class DateAdmin(admin.ModelAdmin):
    list_display = ('date', 'created', 'modified', 'id')
    list_filter = ('date', 'created', 'modified')
admin.site.register(models.Date, DateAdmin)


class LevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'created', 'modified', 'id')
    list_filter = ('level', 'created', 'modified')
admin.site.register(models.Level, LevelAdmin)


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'modified', 'id')
    list_filter = ('created', 'modified')
    search_fields = ('name',)
admin.site.register(models.Organisation, OrganisationAdmin)


class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'modified', 'id')
    list_filter = ('created', 'modified')
    search_fields = ('name',)
admin.site.register(models.Position, PositionAdmin)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'org', 'created', 'modified', 'id')
    list_filter = ('created', 'modified')
    search_fields = ('name', 'org__name')
admin.site.register(models.Employee, EmployeeAdmin)


class PlaceAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'addr',
        'created',
        'modified',
        'id',
    )
    list_filter = ('created', 'modified')
    search_fields = ('name', 'code')
admin.site.register(models.Place, PlaceAdmin)


class ExamAdmin(admin.ModelAdmin):
    list_display = (
        'datafile',
        'date',
        'level',
        'place',
        'employee',
        'position',
        'created',
        'modified',
        'id',
    )
    list_filter = (
        'level', 'datafile__name', 'date__date'
    )
    search_fields = ('date__date', 'place__code', 'place__name', 'employee__name')
admin.site.register(models.Exam, ExamAdmin)


class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'created', 'modified', 'id')
    list_filter = ('name', 'url', 'created', 'modified')
admin.site.register(models.DataSource, DataSourceAdmin)


class DataFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'size', 'last_modified', 'created', 'modified', 'id')
    list_filter = ('name', 'created', 'modified')
admin.site.register(models.DataFile, DataFileAdmin)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee', 'last_send', 'created', 'modified', 'id')
admin.site.register(models.Subscription, SubscriptionAdmin)
