from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import *

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """커스텀 유저 관리자"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'country', 'preferred_language', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'country', 'preferred_language', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('개인 정보', {
            'fields': ('phone_number', 'birth_date', 'country', 'preferred_language', 'passport_number')
        }),
        ('비상 연락처', {
            'fields': ('emergency_contact', 'emergency_phone')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('개인 정보', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'birth_date', 
                      'country', 'preferred_language', 'passport_number', 'emergency_contact', 'emergency_phone')
        }),
    )

@admin.register(MedicalDepartment)
class MedicalDepartmentAdmin(admin.ModelAdmin):
    """진료과목 관리자"""
    list_display = ('name_ko', 'name_en', 'is_popular', 'doctor_count', 'created_at')
    list_filter = ('is_popular', 'created_at')
    search_fields = ('name_ko', 'name_en', 'name_zh', 'name_ja', 'name_ru', 'name_ar')
    list_editable = ('is_popular',)
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name_ko', 'name_en', 'description', 'icon', 'is_popular')
        }),
        ('다국어 이름', {
            'fields': ('name_zh', 'name_ja', 'name_ru', 'name_ar'),
            'classes': ('collapse',)
        }),
    )
    
    def doctor_count(self, obj):
        return obj.doctors.count()
    doctor_count.short_description = '의사 수'

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """의사 관리자"""
    list_display = ('name', 'department', 'specialization', 'experience_years', 'rating', 'is_available')
    list_filter = ('department', 'is_available', 'experience_years')
    search_fields = ('name', 'specialization', 'languages')
    list_editable = ('is_available',)
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'department', 'specialization', 'experience_years', 'languages')
        }),
        ('프로필', {
            'fields': ('profile_image', 'bio', 'consultation_fee', 'is_available', 'rating')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department')

@admin.register(MedicalPackage)
class MedicalPackageAdmin(admin.ModelAdmin):
    """의료패키지 관리자"""
    list_display = ('name_ko', 'department', 'package_type', 'price', 'duration_days', 'is_featured')
    list_filter = ('department', 'package_type', 'is_featured', 'created_at')
    search_fields = ('name_ko', 'name_en', 'description')
    list_editable = ('is_featured',)
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name_ko', 'name_en', 'department', 'package_type', 'is_featured')
        }),
        ('상세 정보', {
            'fields': ('description', 'price', 'duration_days', 'image')
        }),
        ('포함/불포함 사항', {
            'fields': ('includes', 'excludes', 'popular_countries')
        }),
    )

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """예약 관리자"""
    list_display = ('patient_name', 'doctor', 'appointment_date', 'status', 'payment_status', 'total_amount')
    list_filter = ('status', 'payment_status', 'appointment_date', 'doctor__department')
    search_fields = ('patient__username', 'patient__email', 'doctor__name')
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('예약 정보', {
            'fields': ('patient', 'doctor', 'package', 'appointment_date', 'total_amount')
        }),
        ('상태', {
            'fields': ('status', 'payment_status')
        }),
        ('의료 정보', {
            'fields': ('symptoms', 'medical_history', 'allergies', 'medications', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}" if obj.patient.first_name else obj.patient.username
    patient_name.short_description = '환자명'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'doctor', 'package')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """결제 관리자"""
    list_display = ('transaction_id', 'appointment_patient', 'amount', 'currency', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'currency', 'payment_date')
    search_fields = ('transaction_id', 'appointment__patient__username', 'appointment__patient__email')
    readonly_fields = ('transaction_id', 'payment_date')
    
    def appointment_patient(self, obj):
        return f"{obj.appointment.patient.username} - {obj.appointment.doctor.name}"
    appointment_patient.short_description = '예약 정보'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """후기 관리자"""
    list_display = ('title', 'rating', 'patient_name', 'doctor_name', 'recommend', 'created_at')
    list_filter = ('rating', 'recommend', 'created_at', 'appointment__doctor__department')
    search_fields = ('title', 'content', 'appointment__patient__username', 'appointment__doctor__name')
    
    def patient_name(self, obj):
        return obj.appointment.patient.username
    patient_name.short_description = '환자'
    
    def doctor_name(self, obj):
        return obj.appointment.doctor.name
    doctor_name.short_description = '의사'

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    """의사 스케줄 관리자"""
    list_display = ('doctor', 'weekday_display', 'start_time', 'end_time', 'is_available')
    list_filter = ('weekday', 'is_available', 'doctor__department')
    search_fields = ('doctor__name',)
    list_editable = ('is_available',)
    
    def weekday_display(self, obj):
        return obj.get_weekday_display()
    weekday_display.short_description = '요일'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """알림 관리자"""
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    list_editable = ('is_read',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# 관리자 사이트 커스터마이징
admin.site.site_header = "MediCare Global 관리자"
admin.site.site_title = "MediCare Global"
admin.site.index_title = "의료관광 시스템 관리"