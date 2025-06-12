from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid

class CustomUser(AbstractUser):
    """커스텀 유저 모델"""
    COUNTRY_CHOICES = [
        ('KR', '한국'),
        ('US', 'United States'),
        ('CN', '中国'),
        ('JP', '日本'),
        ('RU', 'Россия'),
        ('SA', 'العربية السعودية'),
        ('DE', 'Deutschland'),
        ('FR', 'France'),
        ('GB', 'United Kingdom'),
        ('OTHER', 'Other'),
    ]
    
    LANGUAGE_CHOICES = [
        ('ko', '한국어'),
        ('en', 'English'),
        ('zh', '中文'),
        ('ja', '日本語'),
        ('ru', 'Русский'),
        ('ar', 'العربية'),
        ('de', 'Deutsch'),
        ('fr', 'Français'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="전화번호는 '+999999999' 형식이어야 합니다. 최대 15자리까지 가능합니다."
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, default='KR')
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='ko')
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_country_display()})"

class MedicalDepartment(models.Model):
    """진료과목 모델"""
    name_ko = models.CharField(max_length=100, verbose_name="진료과목명(한국어)")
    name_en = models.CharField(max_length=100, verbose_name="진료과목명(영어)")
    name_zh = models.CharField(max_length=100, blank=True, verbose_name="진료과목명(중국어)")
    name_ja = models.CharField(max_length=100, blank=True, verbose_name="진료과목명(일본어)")
    name_ru = models.CharField(max_length=100, blank=True, verbose_name="진료과목명(러시아어)")
    name_ar = models.CharField(max_length=100, blank=True, verbose_name="진료과목명(아랍어)")
    description = models.TextField(blank=True, verbose_name="설명")
    icon = models.CharField(max_length=50, default='fas fa-stethoscope', verbose_name="아이콘")
    is_popular = models.BooleanField(default=False, verbose_name="인기진료과목")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "진료과목"
        verbose_name_plural = "진료과목들"
    
    def __str__(self):
        return self.name_ko

    def get_name_by_language(self, language):
        """언어별 진료과목명 반환"""
        name_mapping = {
            'ko': self.name_ko,
            'en': self.name_en,
            'zh': self.name_zh or self.name_en,
            'ja': self.name_ja or self.name_en,
            'ru': self.name_ru or self.name_en,
            'ar': self.name_ar or self.name_en,
        }
        return name_mapping.get(language, self.name_en)

class Doctor(models.Model):
    """의사 모델"""
    name = models.CharField(max_length=100, verbose_name="의사명")
    department = models.ForeignKey(MedicalDepartment, on_delete=models.CASCADE, related_name='doctors')
    specialization = models.CharField(max_length=200, verbose_name="전문분야")
    experience_years = models.PositiveIntegerField(verbose_name="경력(년)")
    languages = models.CharField(max_length=100, verbose_name="구사언어")
    profile_image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    bio = models.TextField(blank=True, verbose_name="프로필")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="진료비")
    is_available = models.BooleanField(default=True, verbose_name="진료가능")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="평점")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "의사"
        verbose_name_plural = "의사들"
    
    def __str__(self):
        return f"{self.name} - {self.department.name_ko}"

class MedicalPackage(models.Model):
    """의료관광 패키지 모델"""
    PACKAGE_TYPE_CHOICES = [
        ('basic', '기본 검진'),
        ('premium', '프리미엄 검진'),
        ('cosmetic', '미용 패키지'),
        ('wellness', '웰니스 패키지'),
        ('dental', '치과 패키지'),
    ]
    
    name_ko = models.CharField(max_length=200, verbose_name="패키지명(한국어)")
    name_en = models.CharField(max_length=200, verbose_name="패키지명(영어)")
    department = models.ForeignKey(MedicalDepartment, on_delete=models.CASCADE)
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES, default='basic')
    description = models.TextField(verbose_name="패키지 설명")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="가격")
    duration_days = models.PositiveIntegerField(verbose_name="소요일수")
    includes = models.TextField(verbose_name="포함사항")
    excludes = models.TextField(blank=True, verbose_name="불포함사항")
    popular_countries = models.CharField(max_length=100, blank=True, verbose_name="인기국가")
    image = models.ImageField(upload_to='packages/', blank=True, null=True)
    is_featured = models.BooleanField(default=False, verbose_name="추천 패키지")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "의료패키지"
        verbose_name_plural = "의료패키지들"
    
    def __str__(self):
        return self.name_ko

class Appointment(models.Model):
    """예약 모델"""
    STATUS_CHOICES = [
        ('pending', '예약 대기'),
        ('confirmed', '예약 확정'),
        ('cancelled', '예약 취소'),
        ('completed', '진료 완료'),
        ('no_show', '노쇼'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', '결제 대기'),
        ('paid', '결제 완료'),
        ('refunded', '환불 완료'),
        ('failed', '결제 실패'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    package = models.ForeignKey(MedicalPackage, on_delete=models.CASCADE, null=True, blank=True)
    appointment_date = models.DateTimeField(verbose_name="예약일시")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="총 금액")
    notes = models.TextField(blank=True, verbose_name="특이사항")
    symptoms = models.TextField(blank=True, verbose_name="증상")
    medical_history = models.TextField(blank=True, verbose_name="병력")
    allergies = models.TextField(blank=True, verbose_name="알레르기")
    medications = models.TextField(blank=True, verbose_name="복용약물")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "예약"
        verbose_name_plural = "예약들"
        ordering = ['-appointment_date']
    
    def __str__(self):
        return f"{self.patient.username} - {self.doctor.name} ({self.appointment_date.strftime('%Y-%m-%d %H:%M')})"

class Payment(models.Model):
    """결제 모델"""
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', '신용카드'),
        ('bank_transfer', '계좌이체'),
        ('paypal', 'PayPal'),
        ('wechat', '위챗페이'),
        ('alipay', '알리페이'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="결제금액")
    currency = models.CharField(max_length=3, default='KRW', verbose_name="통화")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name="거래ID")
    payment_date = models.DateTimeField(auto_now_add=True)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="환불금액")
    refund_date = models.DateTimeField(null=True, blank=True, verbose_name="환불일시")
    
    class Meta:
        verbose_name = "결제"
        verbose_name_plural = "결제들"
    
    def __str__(self):
        return f"{self.appointment.patient.username} - {self.amount} {self.currency}"

class Review(models.Model):
    """후기 모델"""
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="평점")
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="후기 내용")
    recommend = models.BooleanField(default=True, verbose_name="추천 여부")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "후기"
        verbose_name_plural = "후기들"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.appointment.patient.username} - {self.rating}★"

class DoctorSchedule(models.Model):
    """의사 스케줄 모델"""
    WEEKDAY_CHOICES = [
        (0, '월요일'),
        (1, '화요일'),
        (2, '수요일'),
        (3, '목요일'),
        (4, '금요일'),
        (5, '토요일'),
        (6, '일요일'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField(verbose_name="시작시간")
    end_time = models.TimeField(verbose_name="종료시간")
    is_available = models.BooleanField(default=True, verbose_name="진료가능")
    
    class Meta:
        verbose_name = "의사 스케줄"
        verbose_name_plural = "의사 스케줄들"
        unique_together = ['doctor', 'weekday', 'start_time']
    
    def __str__(self):
        return f"{self.doctor.name} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"

class Notification(models.Model):
    """알림 모델"""
    TYPE_CHOICES = [
        ('appointment', '예약 관련'),
        ('payment', '결제 관련'),
        ('reminder', '예약 알림'),
        ('system', '시스템 알림'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200, verbose_name="제목")
    message = models.TextField(verbose_name="메시지")
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False, verbose_name="읽음 여부")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "알림"
        verbose_name_plural = "알림들"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"