import sys

from django import forms
from django.contrib import admin
from django.contrib.admin import widgets
from django.core.validators import FileExtensionValidator
from django.shortcuts import redirect, render
from django.urls import path, reverse

from . import models


class DateAdmin(admin.ModelAdmin):
    list_display = ("date", "created", "modified", "id")
    list_filter = ("date", "created", "modified")


admin.site.register(models.Date, DateAdmin)


class LevelAdmin(admin.ModelAdmin):
    list_display = ("level", "created", "modified", "id")
    list_filter = ("level", "created", "modified")


admin.site.register(models.Level, LevelAdmin)


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "modified", "id")
    list_filter = ("created", "modified")
    search_fields = ("name",)


admin.site.register(models.Organisation, OrganisationAdmin)


class PositionAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "modified", "id")
    list_filter = ("created", "modified")
    search_fields = ("name",)


admin.site.register(models.Position, PositionAdmin)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "created", "modified", "id")
    list_filter = ("created", "modified")
    search_fields = ("name", "org__name")


admin.site.register(models.Employee, EmployeeAdmin)


class PlaceAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "addr",
        "created",
        "modified",
        "id",
    )
    list_filter = ("created", "modified")
    search_fields = ("name", "code")


admin.site.register(models.Place, PlaceAdmin)


class ExamImportForm(forms.Form):
    date = forms.ModelChoiceField(queryset=models.Date.objects.all(),)
    level = forms.ModelChoiceField(queryset=models.Level.objects.all(),)
    exam_file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["xlsx"])],
        help_text="Файл в формате .xlsx",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].widget = widgets.RelatedFieldWidgetWrapper(
            self.fields["date"].widget,
            models.Exam._meta.get_field("date").remote_field,
            admin.site,
            can_change_related=True,
        )
        self.fields["level"].widget = widgets.RelatedFieldWidgetWrapper(
            self.fields["level"].widget,
            models.Exam._meta.get_field("level").remote_field,
            admin.site,
            can_change_related=True,
        )


class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "datafile",
        "date",
        "level",
        "place",
        "employee",
        "position",
        "created",
        "modified",
        "id",
    )
    list_filter = ("level", "datafile__name", "date__date")
    search_fields = ("date__date", "place__code", "place__name", "employee__name")

    change_list_template = "admin/exam_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "import/",
                self.admin_site.admin_view(self.exam_import),
                name="exam_import",
            )
        ]
        return my_urls + urls

    def exam_import(self, request):
        info = self.model._meta.app_label, self.model._meta.model_name

        if request.method == "POST":
            form = ExamImportForm(request.POST, request.FILES)
            if form.is_valid():
                exam_file = request.FILES["exam_file"]
                date = form.cleaned_data["date"]
                level = form.cleaned_data["level"]

                # noinspection PyBroadException
                try:
                    self.message_user(
                        request,
                        f"Экзамены из файла '{exam_file.name}' на {date} для {level} класса успешно добавлены",
                    )
                except:  # noqa  # pragma: no cover
                    self.message_user(request, sys.exc_info(), level=40)

                return redirect(reverse("admin:%s_%s_changelist" % info))
        else:
            form = ExamImportForm()

        context = {
            "title": "Импорт экзаменов",
            "app_label": self.model._meta.app_label,
            "opts": self.opts,
            "has_change_permission": self.has_change_permission(request),
            "has_view_permission": self.has_view_permission(request),
            "media": self.media,
            "form": form,
            "adminform": admin.helpers.AdminForm(
                form,
                list([(None, {"fields": form.base_fields})]),
                self.get_prepopulated_fields(request),
            ),
        }

        return render(request, "admin/exam_import_form.html", context)


admin.site.register(models.Exam, ExamAdmin)


class DataSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "created", "modified", "id")
    list_filter = ("name", "url", "created", "modified")


admin.site.register(models.DataSource, DataSourceAdmin)


class DataFileAdmin(admin.ModelAdmin):
    list_display = ("name", "size", "last_modified", "created", "modified", "id")
    list_filter = ("name", "created", "modified")


admin.site.register(models.DataFile, DataFileAdmin)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "employee", "last_send", "created", "modified", "id")


admin.site.register(models.Subscription, SubscriptionAdmin)
