from django.contrib import admin
from .models import PartnerApplication, SellItem, Profile, ContactMessage
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import Property
from .models import SellItem
from .models import PropertyDevelopmentRequest
from django.contrib import admin
from .models import PropertyCategory, PropertyType, RenovationRequest
from .models import Bid
from .models import LoginActivity



admin.site.site_header = "WalBrand Administration"
admin.site.site_title = "WalBrand Admin Portal"
admin.site.index_title = "Welcome to WalBrand Admin"


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    extra = 0
    fields = ("phone", "id_card", "verified")

# Extend UserAdmin to include Profile
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "username", "email", "first_name", "last_name",
        "get_phone", "get_id_card", "get_verified", "is_staff"
    )

    def get_phone(self, obj):
        return obj.profile.phone
    get_phone.short_description = "Phone"

    def get_id_card(self, obj):
        if obj.profile.id_card:
            return format_html('<a href="{}" target="_blank">View ID</a>', obj.profile.id_card.url)
        return "No ID"
    get_id_card.short_description = "ID Card"

    def get_verified(self, obj):
        return "✅ Verified" if obj.profile.verified else "❌ Not Verified"
    get_verified.short_description = "Verified Status"

# Unregister old User admin and register new one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(ContactMessage)


@admin.register(SellItem)
class SellItemAdmin(admin.ModelAdmin):
    # Fields displayed in the list view
    list_display = (
        "title",
        "user",
        "category",
        "house_type",
        "location",
        "price",
        "image_thumbnail",
        "ownership_proof_link",
        "sold_tag",
        "is_sold",
        "created_at",
    )

    list_filter = ("user", "category", "house_type", "created_at")
    search_fields = ("title", "user__username", "description", "location", "is_sold", "sold_tag")
    readonly_fields = ("created_at", "image_preview", "image_thumbnail", "ownership_proof_link")
    list_editable = ("is_sold", )


    # Form fields order
    fields = (
        "user",
        "title",
        "description",
        "price",
        "category",
        "house_type",
        "location",
        "image",
        "image_preview",
        "ownership_proof",          
        "ownership_proof_link", 
        "is_sold",
        "created_at",
    )



    # Preview uploaded image in form
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" />', obj.image.url)
        return "-"
    image_preview.short_description = "Image Preview"

    # Small thumbnail for list view
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" style="border-radius:4px;"/>', obj.image.url)
        return "-"
    image_thumbnail.short_description = "Image"

    def ownership_proof_link(self, obj):
        if obj.ownership_proof and obj.ownership_proof.name.lower().endswith((".png", ".jpg", ".jpeg")):
            return format_html('<img src="{}" width="100" />', obj.ownership_proof.url)
        elif obj.ownership_proof:
            return format_html('<a href="{}" target="_blank">View</a>', obj.ownership_proof.url)
        return "-"

    def sold_tag(self, obj):
        if obj.is_sold:
            return format_html('<span style="color: red; font-weight: bold;">SOLD</span>')
        return ""
    sold_tag.short_description = "Status"
    



@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "commission", "final_price", "user", "is_sold", "sold_tag", "created_at")
    readonly_fields = ("commission", "final_price")

    def sold_tag(self, obj):
        if obj.is_sold:
            return format_html('<span style="color: red; font-weight: bold;">SOLD</span>')
        return ""
    sold_tag.short_description = "Status"





@admin.register(PartnerApplication)
class PartnerApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "submitted_at")
    search_fields = ("name", "email", "company")
    list_filter = ("submitted_at",)
    ordering = ("-submitted_at",)



class PropertyTypeInline(admin.TabularInline):
    model = PropertyType
    extra = 1






@admin.register(PropertyDevelopmentRequest)
class PropertyDevelopmentRequestAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "phone",             
        "property_type",
        "residential_type",
        "commercial_type",
        "land_type",
        "phone",
        "submitted_at",
    )
    list_filter = ("property_type", "submitted_at")
    search_fields = ("full_name", "email", "phone", "details") 
    ordering = ("-submitted_at",)





@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("user", "get_item", "amount", "status", "created_at")
    list_filter = ("status",  )  # filter by status and type
    search_fields = ("user__username",)

    actions = ["accept_bids", "reject_bids"]

    def get_item(self, obj):
        return obj.property.title
    get_item.short_description = "Property"


    def accept_bids(self, request, queryset):
        updated = queryset.update(status="accepted")
        self.message_user(request, f"{updated} bids marked as Accepted.")
    accept_bids.short_description = "Accept selected bids"

    def reject_bids(self, request, queryset):
        updated = queryset.update(status="rejected")
        self.message_user(request, f"{updated} bids marked as Rejected.")
    reject_bids.short_description = "Reject selected bids"


@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'browser', 'os', 'device_type', 'login_time', 'login_success')
    list_filter = ('login_success', 'browser', 'os', 'device_type')
    search_fields = ('user__username', 'ip_address', 'browser', 'os')

