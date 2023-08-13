import sys
from urllib.parse import urlparse

from django import forms
from django.contrib import admin
from django.contrib.admin import widgets
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
    exclude = ("search_vector",)


admin.site.register(models.Organisation, OrganisationAdmin)


class PositionAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "modified", "id")
    list_filter = ("created", "modified")
    search_fields = ("name",)
    exclude = ("search_vector",)


admin.site.register(models.Position, PositionAdmin)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "created", "modified", "id")
    list_filter = ("created", "modified")
    search_fields = ("name", "org__name")
    exclude = ("search_vector",)


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
    exclude = ("search_vector",)


admin.site.register(models.Place, PlaceAdmin)


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


def datafile_url_validator(value):
    domain = "rcoi.mcko.ru"
    ext = ".xlsx"
    url = urlparse(value)
    if url.netloc != domain:
        raise forms.ValidationError(f"Ссылка должна вести на сайт {domain}")
    if not url.path.endswith(ext):
        raise forms.ValidationError(f"Ссылка должна заканчиваться на {ext}")


class ExamImportForm(forms.Form):
    date = forms.ModelChoiceField(
        queryset=models.Date.objects.all(), help_text="Дата экзамена"
    )
    level = forms.ModelChoiceField(
        queryset=models.Level.objects.all(), help_text="Уровень экзамена"
    )
    datafile_url = forms.URLField(
        widget=forms.URLInput(attrs={"class": "vURLField"}),
        help_text="Ссылка с сайта rcoi.mcko.ru на файл в формате .xlsx",
        validators=[datafile_url_validator],
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
        app_label, model_name = self.model._meta.app_label, self.model._meta.model_name

        if request.method == "POST":
            form = ExamImportForm(request.POST, request.FILES)

            if form.is_valid():
                data = {
                    "date": form.cleaned_data["date"].date,
                    "level": form.cleaned_data["level"].level,
                    "datafile_url": form.cleaned_data["datafile_url"],
                }
                datafile_name = urlparse(data["datafile_url"]).path.split("/")[-1]

                try:
                    models.ExamImporter(**data).run()
                    self.message_user(
                        request,
                        f"Файл {datafile_name} обработан",
                    )
                except Exception:
                    self.message_user(request, sys.exc_info(), level=40)

                return redirect(reverse(f"admin:{app_label}_{model_name}_changelist"))
        else:
            form = ExamImportForm()

        context = {
            "add": True,
            "title": "Импорт экзаменов",
            "app_label": app_label,
            "opts": self.opts,
            "has_view_permission": self.has_view_permission(request),
            "has_add_permission": self.has_add_permission(request),
            "has_change_permission": self.has_change_permission(request),
            "has_delete_permission": self.has_delete_permission(request),
            "media": self.media,
            "form": form,
            "adminform": admin.helpers.AdminForm(
                form,
                [(None, {"fields": form.base_fields})],
                self.get_prepopulated_fields(request),
            ),
        }

        context.update({"has_file_field": context["adminform"].form.is_multipart()})

        return render(request, "admin/exam_import_form.html", context)


admin.site.register(models.Exam, ExamAdmin)
