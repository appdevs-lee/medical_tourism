from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.utils.translation import gettext as _, activate
from datetime import datetime, timedelta, time
import json

from .models import *
from .forms import *

class HomeView(TemplateView):
    """메인 페이지"""
    template_name = 'medical_tourism/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'featured_packages': MedicalPackage.objects.filter(is_featured=True)[:6],
            'popular_departments': MedicalDepartment.objects.filter(is_popular=True)[:8],
            'top_doctors': Doctor.objects.filter(is_available=True).order_by('-rating')[:6],
            'recent_reviews': Review.objects.select_related('appointment__doctor', 'appointment__patient').order_by('-created_at')[:4],
        })
        return context

class RegisterView(CreateView):
    """회원가입"""
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('medical_tourism:home')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, _('회원가입이 완료되었습니다.'))
        return super().form_valid(form)

class CustomLoginView(LoginView):
    """로그인"""
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('medical_tourism:home')

class ProfileView(LoginRequiredMixin, DetailView):
    """프로필 조회"""
    model = CustomUser
    template_name = 'medical_tourism/profile.html'
    context_object_name = 'user_profile'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'appointments': Appointment.objects.filter(patient=self.request.user).order_by('-appointment_date')[:5],
            'notifications': Notification.objects.filter(user=self.request.user, is_read=False)[:5],
        })
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """프로필 수정"""
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'medical_tourism/profile_update.html'
    success_url = reverse_lazy('medical_tourism:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, _('프로필이 성공적으로 업데이트되었습니다.'))
        return super().form_valid(form)

class DepartmentListView(ListView):
    """진료과목 목록"""
    model = MedicalDepartment
    template_name = 'medical_tourism/department_list.html'
    context_object_name = 'departments'
    paginate_by = 12

class DepartmentDetailView(DetailView):
    """진료과목 상세"""
    model = MedicalDepartment
    template_name = 'medical_tourism/department_detail.html'
    context_object_name = 'department'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        department = self.get_object()
        context.update({
            'doctors': Doctor.objects.filter(department=department, is_available=True).order_by('-rating'),
            'packages': MedicalPackage.objects.filter(department=department),
        })
        return context

class DoctorListView(ListView):
    """의사 목록"""
    model = Doctor
    template_name = 'medical_tourism/doctor_list.html'
    context_object_name = 'doctors'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Doctor.objects.filter(is_available=True).select_related('department')
        
        # 필터링
        department_id = self.request.GET.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        language = self.request.GET.get('language')
        if language:
            queryset = queryset.filter(languages__icontains=language)
        
        # 정렬
        sort_by = self.request.GET.get('sort', '-rating')
        queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = MedicalDepartment.objects.all()
        return context

class DoctorDetailView(DetailView):
    """의사 상세 정보"""
    model = Doctor
    template_name = 'medical_tourism/doctor_detail.html'
    context_object_name = 'doctor'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.get_object()
        context.update({
            'reviews': Review.objects.filter(appointment__doctor=doctor).order_by('-created_at')[:5],
            'schedules': DoctorSchedule.objects.filter(doctor=doctor, is_available=True),
        })
        return context

class PackageListView(ListView):
    """패키지 목록"""
    model = MedicalPackage
    template_name = 'medical_tourism/package_list.html'
    context_object_name = 'packages'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = MedicalPackage.objects.select_related('department')
        
        # 필터링
        department_id = self.request.GET.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        package_type = self.request.GET.get('type')
        if package_type:
            queryset = queryset.filter(package_type=package_type)
        
        # 가격 범위 필터
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset.order_by('-is_featured', '-created_at')

class PackageDetailView(DetailView):
    """패키지 상세"""
    model = MedicalPackage
    template_name = 'medical_tourism/package_detail.html'
    context_object_name = 'package'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        package = self.get_object()
        context.update({
            'available_doctors': Doctor.objects.filter(
                department=package.department, 
                is_available=True
            ).order_by('-rating'),
        })
        return context

class AppointmentCreateView(LoginRequiredMixin, CreateView):
    """예약 생성"""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'medical_tourism/appointment_create.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        
        # URL에서 의사나 패키지 정보 가져오기
        doctor_id = self.kwargs.get('doctor_id')
        package_id = self.kwargs.get('package_id')
        
        if doctor_id:
            kwargs['initial_doctor'] = get_object_or_404(Doctor, id=doctor_id)
        if package_id:
            kwargs['initial_package'] = get_object_or_404(MedicalPackage, id=package_id)
        
        return kwargs
    
    def form_valid(self, form):
        form.instance.patient = self.request.user
        messages.success(self.request, _('예약이 성공적으로 생성되었습니다.'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('medical_tourism:payment', kwargs={'appointment_id': self.object.id})

class AppointmentListView(LoginRequiredMixin, ListView):
    """예약 목록"""
    model = Appointment
    template_name = 'medical_tourism/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 10
    
    def get_queryset(self):
        return Appointment.objects.filter(
            patient=self.request.user
        ).select_related('doctor', 'package').order_by('-appointment_date')

class AppointmentDetailView(LoginRequiredMixin, DetailView):
    """예약 상세"""
    model = Appointment
    template_name = 'medical_tourism/appointment_detail.html'
    context_object_name = 'appointment'
    
    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user)

class AppointmentCancelView(LoginRequiredMixin, UpdateView):
    """예약 취소"""
    model = Appointment
    fields = []
    template_name = 'medical_tourism/appointment_cancel.html'
    
    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user, status='confirmed')
    
    def form_valid(self, form):
        appointment = form.instance
        appointment.status = 'cancelled'
        appointment.save()
        
        # 환불 처리 로직 추가 (실제 구현시)
        messages.success(self.request, _('예약이 취소되었습니다.'))
        return redirect('medical_tourism:appointment_list')

class PaymentView(LoginRequiredMixin, TemplateView):
    """결제 페이지"""
    template_name = 'medical_tourism/payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment_id = self.kwargs['appointment_id']
        appointment = get_object_or_404(
            Appointment, 
            id=appointment_id, 
            patient=self.request.user,
            payment_status='pending'
        )
        context['appointment'] = appointment
        return context

class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    """결제 성공"""
    template_name = 'medical_tourism/payment_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment_id = self.kwargs['appointment_id']
        appointment = get_object_or_404(Appointment, id=appointment_id, patient=self.request.user)
        context['appointment'] = appointment
        return context

class PaymentCancelView(LoginRequiredMixin, TemplateView):
    """결제 취소"""
    template_name = 'medical_tourism/payment_cancel.html'

class ReviewListView(ListView):
    """후기 목록"""
    model = Review
    template_name = 'medical_tourism/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10
    ordering = ['-created_at']

class ReviewCreateView(LoginRequiredMixin, CreateView):
    """후기 작성"""
    model = Review
    form_class = ReviewForm
    template_name = 'medical_tourism/review_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment_id = self.kwargs['appointment_id']
        appointment = get_object_or_404(
            Appointment, 
            id=appointment_id, 
            patient=self.request.user,
            status='completed'
        )
        context['appointment'] = appointment
        return context
    
    def form_valid(self, form):
        appointment_id = self.kwargs['appointment_id']
        appointment = get_object_or_404(
            Appointment, 
            id=appointment_id, 
            patient=self.request.user,
            status='completed'
        )
        form.instance.appointment = appointment
        messages.success(self.request, _('후기가 성공적으로 등록되었습니다.'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('medical_tourism:appointment_detail', kwargs={'pk': self.kwargs['appointment_id']})

class NotificationListView(LoginRequiredMixin, ListView):
    """알림 목록"""
    model = Notification
    template_name = 'medical_tourism/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class SearchView(ListView):
    """검색 결과"""
    template_name = 'medical_tourism/search.html'
    context_object_name = 'search_results'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', 'all')
        
        results = []
        
        if query:
            if search_type in ['all', 'doctors']:
                doctors = Doctor.objects.filter(
                    Q(name__icontains=query) |
                    Q(specialization__icontains=query) |
                    Q(department__name_ko__icontains=query) |
                    Q(department__name_en__icontains=query),
                    is_available=True
                ).select_related('department')
                
                for doctor in doctors:
                    results.append({
                        'type': 'doctor',
                        'object': doctor,
                        'title': doctor.name,
                        'subtitle': f"{doctor.department.name_ko} | {doctor.specialization}",
                        'url': reverse('medical_tourism:doctor_detail', kwargs={'pk': doctor.pk})
                    })
            
            if search_type in ['all', 'packages']:
                packages = MedicalPackage.objects.filter(
                    Q(name_ko__icontains=query) |
                    Q(name_en__icontains=query) |
                    Q(description__icontains=query) |
                    Q(department__name_ko__icontains=query)
                ).select_related('department')
                
                for package in packages:
                    results.append({
                        'type': 'package',
                        'object': package,
                        'title': package.name_ko,
                        'subtitle': f"{package.department.name_ko} | {package.price:,}원",
                        'url': reverse('medical_tourism:package_detail', kwargs={'pk': package.pk})
                    })
            
            if search_type in ['all', 'departments']:
                departments = MedicalDepartment.objects.filter(
                    Q(name_ko__icontains=query) |
                    Q(name_en__icontains=query) |
                    Q(description__icontains=query)
                )
                
                for dept in departments:
                    results.append({
                        'type': 'department',
                        'object': dept,
                        'title': dept.name_ko,
                        'subtitle': dept.description[:100] + '...' if len(dept.description) > 100 else dept.description,
                        'url': reverse('medical_tourism:department_detail', kwargs={'pk': dept.pk})
                    })
        
        return results
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'query': self.request.GET.get('q', ''),
            'search_type': self.request.GET.get('type', 'all'),
        })
        return context

# AJAX 뷰들
@login_required
def get_available_slots(request):
    """예약 가능한 시간 슬롯 조회"""
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    
    if not doctor_id or not date_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        doctor = Doctor.objects.get(id=doctor_id, is_available=True)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        weekday = date.weekday()
        
        # 의사의 해당 요일 스케줄 조회
        schedules = DoctorSchedule.objects.filter(
            doctor=doctor,
            weekday=weekday,
            is_available=True
        )
        
        # 이미 예약된 시간 조회
        booked_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__date=date,
            status__in=['pending', 'confirmed']
        ).values_list('appointment_date__time', flat=True)
        
        available_slots = []
        for schedule in schedules:
            current_time = datetime.combine(date, schedule.start_time)
            end_time = datetime.combine(date, schedule.end_time)
            
            while current_time < end_time:
                if current_time.time() not in booked_appointments:
                    available_slots.append({
                        'time': current_time.strftime('%H:%M'),
                        'datetime': current_time.strftime('%Y-%m-%d %H:%M')
                    })
                current_time += timedelta(minutes=30)  # 30분 간격
        
        return JsonResponse({'slots': available_slots})
    
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

def get_doctor_schedule(request, pk):
    """의사 스케줄 조회"""
    doctor = get_object_or_404(Doctor, pk=pk, is_available=True)
    schedules = DoctorSchedule.objects.filter(doctor=doctor, is_available=True)
    
    schedule_data = []
    for schedule in schedules:
        schedule_data.append({
            'weekday': schedule.weekday,
            'weekday_name': schedule.get_weekday_display(),
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M'),
        })
    
    return JsonResponse({'schedules': schedule_data})

@login_required
def mark_notification_read(request, pk):
    """알림 읽음 처리"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})

def set_language(request, language):
    """언어 설정"""
    activate(language)
    request.session['django_language'] = language
    
    # 사용자가 로그인되어 있으면 선호 언어 업데이트
    if request.user.is_authenticated:
        request.user.preferred_language = language
        request.user.save(update_fields=['preferred_language'])
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# 정적 페이지들
def about(request):
    """병원 소개"""
    return render(request, 'medical_tourism/about.html')

def contact(request):
    """연락처"""
    return render(request, 'medical_tourism/contact.html')

def faq(request):
    """자주 묻는 질문"""
    return render(request, 'medical_tourism/faq.html')

def terms(request):
    """이용약관"""
    return render(request, 'medical_tourism/terms.html')

def privacy(request):
    """개인정보처리방침"""
    return render(request, 'medical_tourism/privacy.html')