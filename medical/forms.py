from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import datetime, date, timedelta
from .models import *

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """커스텀 회원가입 폼"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': _('이메일 주소')
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': _('이름')
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': _('성')
        })
    )
    
    phone_number = forms.CharField(
        max_length=17,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': _('전화번호 (+82-10-1234-5678)')
        })
    )
    
    birth_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'type': 'date'
        })
    )
    
    country = forms.ChoiceField(
        choices=CustomUser.COUNTRY_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    
    preferred_language = forms.ChoiceField(
        choices=CustomUser.LANGUAGE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    
    passport_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': _('여권번호 (선택사항)')
        })
    )
    
    emergency_contact = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': _('비상연락처 이름')
        })
    )
    
    emergency_phone = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': _('비상연락처 전화번호')
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 
                 'birth_date', 'country', 'preferred_language', 'passport_number',
                 'emergency_contact', 'emergency_phone', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': _('사용자명')
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': _('비밀번호')
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': _('비밀번호 확인')
        })
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            age = (date.today() - birth_date).days / 365.25
            if age < 18:
                raise ValidationError(_('18세 이상만 가입할 수 있습니다.'))
            if age > 120:
                raise ValidationError(_('올바른 생년월일을 입력해주세요.'))
        return birth_date
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.birth_date = self.cleaned_data['birth_date']
        user.country = self.cleaned_data['country']
        user.preferred_language = self.cleaned_data['preferred_language']
        user.passport_number = self.cleaned_data['passport_number']
        user.emergency_contact = self.cleaned_data['emergency_contact']
        user.emergency_phone = self.cleaned_data['emergency_phone']
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    """프로필 업데이트 폼"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'birth_date',
                 'country', 'preferred_language', 'passport_number', 
                 'emergency_contact', 'emergency_phone')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'country': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'preferred_language': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'passport_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'emergency_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
        }

class AppointmentForm(forms.ModelForm):
    """예약 생성 폼"""
    appointment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'type': 'datetime-local'
        }),
        label=_('예약 날짜 및 시간')
    )
    
    class Meta:
        model = Appointment
        fields = ('doctor', 'package', 'appointment_date', 'symptoms', 
                 'medical_history', 'allergies', 'medications', 'notes')
        widgets = {
            'doctor': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'package': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'symptoms': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': _('현재 증상을 자세히 설명해 주세요.')
            }),
            'medical_history': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': _('과거 병력이나 수술 이력을 알려주세요.')
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': _('알레르기가 있다면 알려주세요.')
            }),
            'medications': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': _('현재 복용 중인 약물이 있다면 알려주세요.')
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': _('기타 특이사항이나 요청사항을 알려주세요.')
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.initial_doctor = kwargs.pop('initial_doctor', None)
        self.initial_package = kwargs.pop('initial_package', None)
        super().__init__(*args, **kwargs)
        
        # 사용 가능한 의사만 표시
        self.fields['doctor'].queryset = Doctor.objects.filter(is_available=True)
        
        # 초기값 설정
        if self.initial_doctor:
            self.fields['doctor'].initial = self.initial_doctor
            self.fields['doctor'].widget.attrs['readonly'] = True
            
        if self.initial_package:
            self.fields['package'].initial = self.initial_package
            self.fields['package'].widget.attrs['readonly'] = True
            # 패키지가 선택되면 해당 진료과의 의사만 표시
            self.fields['doctor'].queryset = Doctor.objects.filter(
                department=self.initial_package.department,
                is_available=True
            )
    
    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date:
            # 과거 날짜 예약 불가
            if appointment_date <= timezone.now():
                raise ValidationError(_('예약은 현재 시간 이후로만 가능합니다.'))
            
            # 너무 먼 미래 예약 불가 (3개월 이내)
            if appointment_date > timezone.now() + timedelta(days=90):
                raise ValidationError(_('예약은 3개월 이내로만 가능합니다.'))
            
            # 의사의 근무시간 확인
            doctor = self.cleaned_data.get('doctor')
            if doctor:
                weekday = appointment_date.weekday()
                time = appointment_date.time()
                
                # 의사의 해당 요일 스케줄 확인
                schedules = DoctorSchedule.objects.filter(
                    doctor=doctor,
                    weekday=weekday,
                    is_available=True,
                    start_time__lte=time,
                    end_time__gt=time
                )
                
                if not schedules.exists():
                    raise ValidationError(_('선택한 시간은 의사의 진료시간이 아닙니다.'))
                
                # 이미 예약된 시간인지 확인
                existing_appointment = Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date=appointment_date,
                    status__in=['pending', 'confirmed']
                ).exists()
                
                if existing_appointment:
                    raise ValidationError(_('선택한 시간은 이미 예약되어 있습니다.'))
        
        return appointment_date
    
    def save(self, commit=True):
        appointment = super().save(commit=False)
        
        # 총 금액 계산
        total_amount = 0
        if appointment.doctor:
            total_amount += appointment.doctor.consultation_fee
        if appointment.package:
            total_amount += appointment.package.price
        
        appointment.total_amount = total_amount
        
        if commit:
            appointment.save()
        return appointment

class ReviewForm(forms.ModelForm):
    """후기 작성 폼"""
    class Meta:
        model = Review
        fields = ('rating', 'title', 'content', 'recommend')
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i}★') for i in range(1, 6)],
                attrs={
                    'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                }
            ),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': _('후기 제목을 입력해주세요.')
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 5,
                'placeholder': _('진료 경험을 자세히 알려주세요.')
            }),
            'recommend': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
        }
        labels = {
            'rating': _('평점'),
            'title': _('제목'),
            'content': _('후기 내용'),
            'recommend': _('다른 분들께 추천하시겠습니까?'),
        }

class SearchForm(forms.Form):
    """검색 폼"""
    SEARCH_TYPE_CHOICES = [
        ('all', _('전체')),
        ('doctors', _('의사')),
        ('packages', _('패키지')),
        ('departments', _('진료과목')),
    ]
    
    q = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': _('검색어를 입력하세요...')
        }),
        label=''
    )
    
    type = forms.ChoiceField(
        choices=SEARCH_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'px-4 py-3 border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        }),
        label=''
    )