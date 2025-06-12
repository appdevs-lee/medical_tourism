from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .views import *

app_name = 'medical_tourism'

urlpatterns = [
    # 메인 페이지
    path('', HomeView.as_view(), name='home'),
    
    # 언어 설정
    path('set-language/<str:language>/', views.set_language, name='set_language'),
    
    # 인증 관련
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='medical_tourism:home'), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    
    # 진료과목 관련
    path('departments/', DepartmentListView.as_view(), name='department_list'),
    path('departments/<int:pk>/', DepartmentDetailView.as_view(), name='department_detail'),
    
    # 의사 관련
    path('doctors/', DoctorListView.as_view(), name='doctor_list'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor_detail'),
    path('doctors/<int:pk>/schedule/', views.get_doctor_schedule, name='doctor_schedule'),
    
    # 패키지 관련
    path('packages/', PackageListView.as_view(), name='package_list'),
    path('packages/<int:pk>/', PackageDetailView.as_view(), name='package_detail'),
    
    # 예약 관련
    path('appointment/book/', AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointment/book/<int:doctor_id>/', AppointmentCreateView.as_view(), name='appointment_create_doctor'),
    path('appointment/book/<int:doctor_id>/<int:package_id>/', AppointmentCreateView.as_view(), name='appointment_create_package'),
    path('appointments/', AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/<uuid:pk>/', AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/<uuid:pk>/cancel/', AppointmentCancelView.as_view(), name='appointment_cancel'),
    
    # 예약 가능 시간 조회 (AJAX)
    path('api/available-slots/', views.get_available_slots, name='available_slots'),
    
    # 결제 관련
    path('payment/<uuid:appointment_id>/', PaymentView.as_view(), name='payment'),
    path('payment/<uuid:appointment_id>/success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/<uuid:appointment_id>/cancel/', PaymentCancelView.as_view(), name='payment_cancel'),
    
    # 후기 관련
    path('reviews/', ReviewListView.as_view(), name='review_list'),
    path('appointments/<uuid:appointment_id>/review/', ReviewCreateView.as_view(), name='review_create'),
    
    # 알림 관련
    path('notifications/', NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='notification_read'),
    
    # 검색
    path('search/', SearchView.as_view(), name='search'),
    
    # 정적 페이지
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
]