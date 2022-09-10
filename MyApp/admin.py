from django.contrib import admin

from . import models as m

# Register your models here.


admin.site.register(m.Donation)
admin.site.register(m.Category)


@admin.register(m.ExtendedUser)
class SuperUser(admin.ModelAdmin):
    list_filter = ("is_superuser",)
    list_display = ('username', 'first_name', 'last_name', 'is_superuser',)
    ordering = ("username",)
    search_fields = ("last_name__icontains", "first_name__icontains",)
    change_form_template = 'MyApp/admin/custom_change_form.html'

    def _changeform_view(self, request, object_id, form_url, extra_context):
        extra_context = {
            "display_delete_button": False if str(request.user.pk) == object_id
                                     else True
        }

        return super(SuperUser, self)._changeform_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context
        )


@admin.register(m.Institution)
class TrustedInstitutions(admin.ModelAdmin):
    list_filter = ("is_trusted",)
    list_display = ('name', 'description', 'type', 'is_trusted',)
    search_fields = ("name__icontains",)
