from django.contrib import admin
from .models import Date, Level, Organisation, Position, Employee, Territory, Place, Exam


class DateAdmin(admin.ModelAdmin):
    list_display = ('date', 'created', 'modified', 'id')
    list_filter = ('date', 'created', 'modified')
admin.site.register(Date, DateAdmin)


class LevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'created', 'modified', 'id')
    list_filter = ('level', 'created', 'modified')
admin.site.register(Level, LevelAdmin)


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'modified', 'id')
    list_filter = ('created', 'modified')
    search_fields = ('name',)
admin.site.register(Organisation, OrganisationAdmin)


class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'modified', 'id')
    list_filter = ('created', 'modified')
    search_fields = ('name',)
admin.site.register(Position, PositionAdmin)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'org', 'created', 'modified', 'id')
    list_filter = ('created', 'modified')
    search_fields = ('name', 'org__name')
admin.site.register(Employee, EmployeeAdmin)


class TerritoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created', 'modified', 'id')
    list_filter = ('code', 'created', 'modified')
    search_fields = ('name', 'code')
admin.site.register(Territory, TerritoryAdmin)


class PlaceAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'addr',
        'ate',
        'created',
        'modified',
        'id',
    )
    list_filter = ('ate', 'created', 'modified')
    search_fields = ('name', 'code')
admin.site.register(Place, PlaceAdmin)


class ExamAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'level',
        'place',
        'employee',
        'get_employee_pos',
        'created',
        'modified',
        'id',
    )
    list_filter = (
        'level', 'date__date', 'place__code'
    )
    search_fields = ('date__date', 'place__code', 'place__name', 'employee__name')

    def get_employee_pos(self, obj):
        return obj.employee.position

    get_employee_pos.short_description = 'Должность в ППЭ'
    get_employee_pos.admin_order_field = 'employee__position'
admin.site.register(Exam, ExamAdmin)
