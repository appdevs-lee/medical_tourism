# medical_tourism/management/__init__.py
# 빈 파일

# medical_tourism/management/commands/__init__.py  
# 빈 파일

# medical_tourism/management/commands/create_sample_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random
from decimal import Decimal

from medical.models import (
    MedicalDepartment, Doctor, MedicalPackage, Appointment, 
    Payment, Review, DoctorSchedule, Notification, CustomUser
)

User = get_user_model()

class Command(BaseCommand):
    help = '가상 데이터를 생성합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users', type=int, default=20,
            help='생성할 사용자 수 (기본값: 20)'
        )
        parser.add_argument(
            '--doctors', type=int, default=15,
            help='생성할 의사 수 (기본값: 15)'
        )
        parser.add_argument(
            '--appointments', type=int, default=50,
            help='생성할 예약 수 (기본값: 50)'
        )

    def handle(self, *args, **options):
        self.stdout.write('가상 데이터 생성을 시작합니다...')
        
        # 기존 데이터 삭제 (선택적)
        if input('기존 데이터를 삭제하시겠습니까? (y/N): ').lower() == 'y':
            self.clear_data()
        
        # 데이터 생성
        self.create_departments()
        self.create_packages()
        self.create_users(options['users'])
        self.create_doctors(options['doctors'])
        self.create_doctor_schedules()
        self.create_appointments(options['appointments'])
        self.create_reviews()
        self.create_notifications()
        
        self.stdout.write(
            self.style.SUCCESS('가상 데이터 생성이 완료되었습니다!')
        )

    def clear_data(self):
        """기존 데이터 삭제"""
        self.stdout.write('기존 데이터를 삭제합니다...')
        
        # 순서 중요 (외래키 관계 고려)
        Notification.objects.all().delete()
        Review.objects.all().delete()
        Payment.objects.all().delete()
        Appointment.objects.all().delete()
        DoctorSchedule.objects.all().delete()
        Doctor.objects.all().delete()
        MedicalPackage.objects.all().delete()
        MedicalDepartment.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_departments(self):
        """진료과목 생성"""
        self.stdout.write('진료과목 데이터를 생성합니다...')
        
        departments_data = [
            {
                'name_ko': '내과', 'name_en': 'Internal Medicine', 
                'name_zh': '内科', 'name_ja': '内科',
                'icon': 'fas fa-stethoscope', 'is_popular': True,
                'description': '일반적인 내과 질환의 진단과 치료를 담당합니다.'
            },
            {
                'name_ko': '외과', 'name_en': 'Surgery',
                'name_zh': '外科', 'name_ja': '外科', 
                'icon': 'fas fa-cut', 'is_popular': True,
                'description': '수술을 통한 질병 치료를 전문으로 합니다.'
            },
            {
                'name_ko': '성형외과', 'name_en': 'Plastic Surgery',
                'name_zh': '整形外科', 'name_ja': '形成外科',
                'icon': 'fas fa-magic', 'is_popular': True,
                'description': '미용 성형 및 재건 수술을 전문으로 합니다.'
            },
            {
                'name_ko': '피부과', 'name_en': 'Dermatology',
                'name_zh': '皮肤科', 'name_ja': '皮膚科',
                'icon': 'fas fa-hand-paper', 'is_popular': True,
                'description': '피부 질환 치료 및 미용 관리를 제공합니다.'
            },
            {
                'name_ko': '치과', 'name_en': 'Dentistry',
                'name_zh': '牙科', 'name_ja': '歯科',
                'icon': 'fas fa-tooth', 'is_popular': True,
                'description': '구강 건강 관리 및 치료를 담당합니다.'
            },
            {
                'name_ko': '안과', 'name_en': 'Ophthalmology',
                'name_zh': '眼科', 'name_ja': '眼科',
                'icon': 'fas fa-eye', 'is_popular': False,
                'description': '눈 질환의 진단과 치료를 전문으로 합니다.'
            },
            {
                'name_ko': '이비인후과', 'name_en': 'ENT',
                'name_zh': '耳鼻喉科', 'name_ja': '耳鼻咽喉科',
                'icon': 'fas fa-head-side-mask', 'is_popular': False,
                'description': '귀, 코, 목 질환을 치료합니다.'
            },
            {
                'name_ko': '정형외과', 'name_en': 'Orthopedics',
                'name_zh': '骨科', 'name_ja': '整形外科',
                'icon': 'fas fa-bone', 'is_popular': True,
                'description': '뼈와 관절 질환을 치료합니다.'
            },
            {
                'name_ko': '산부인과', 'name_en': 'Obstetrics & Gynecology',
                'name_zh': '妇产科', 'name_ja': '産婦人科',
                'icon': 'fas fa-baby', 'is_popular': False,
                'description': '여성 건강과 출산을 담당합니다.'
            },
            {
                'name_ko': '신경외과', 'name_en': 'Neurosurgery',
                'name_zh': '神经外科', 'name_ja': '脳神経外科',
                'icon': 'fas fa-brain', 'is_popular': False,
                'description': '뇌와 신경계 수술을 전문으로 합니다.'
            }
        ]
        
        for dept_data in departments_data:
            MedicalDepartment.objects.get_or_create(**dept_data)

    def create_packages(self):
        """의료 패키지 생성"""
        self.stdout.write('의료 패키지 데이터를 생성합니다...')
        
        departments = MedicalDepartment.objects.all()
        
        packages_data = [
            {
                'name_ko': '프리미엄 건강검진 패키지',
                'name_en': 'Premium Health Checkup Package',
                'package_type': 'premium',
                'price': Decimal('2500000'),
                'duration_days': 3,
                'includes': '종합건강검진, MRI, CT, 혈액검사, 영양상담, 개인병실',
                'excludes': '항공료, 숙박비',
                'popular_countries': 'CN,JP,US',
                'is_featured': True,
                'description': '최첨단 장비를 이용한 종합적인 건강검진 서비스입니다.'
            },
            {
                'name_ko': '성형외과 올인원 패키지',
                'name_en': 'Plastic Surgery All-in-One Package',
                'package_type': 'cosmetic',
                'price': Decimal('8000000'),
                'duration_days': 7,
                'includes': '수술, 회복실, 사후관리, 통역서비스, 픽업서비스',
                'excludes': '숙박비, 식비',
                'popular_countries': 'CN,JP,RU',
                'is_featured': True,
                'description': '안전하고 만족스러운 성형수술 전 과정을 관리합니다.'
            },
            {
                'name_ko': '피부 미용 관리 패키지',
                'name_en': 'Skin Care Beauty Package',
                'package_type': 'cosmetic',
                'price': Decimal('1200000'),
                'duration_days': 5,
                'includes': '레이저 시술, 관리실, 화장품, 애프터케어',
                'excludes': '항공료, 숙박비',
                'popular_countries': 'CN,JP,SA',
                'is_featured': True,
                'description': '최신 레이저 기술로 아름다운 피부를 만들어드립니다.'
            },
            {
                'name_ko': '치과 임플란트 패키지',
                'name_en': 'Dental Implant Package',
                'package_type': 'dental',
                'price': Decimal('3500000'),
                'duration_days': 14,
                'includes': '임플란트 수술, 보철물, 경과관찰, 통역서비스',
                'excludes': '숙박비, 식비',
                'popular_countries': 'CN,RU,US',
                'is_featured': False,
                'description': '최고급 임플란트로 자연스러운 치아를 되찾아드립니다.'
            },
            {
                'name_ko': '웰니스 힐링 패키지',
                'name_en': 'Wellness Healing Package',
                'package_type': 'wellness',
                'price': Decimal('1800000'),
                'duration_days': 5,
                'includes': '스파, 마사지, 건강상담, 영양관리, 요가클래스',
                'excludes': '항공료',
                'popular_countries': 'JP,US,DE',
                'is_featured': True,
                'description': '몸과 마음의 완전한 휴식과 회복을 제공합니다.'
            }
        ]
        
        for pkg_data in packages_data:
            if departments:
                # 패키지 타입에 따라 적절한 진료과 선택
                if pkg_data['package_type'] == 'cosmetic':
                    dept = departments.filter(name_ko__in=['성형외과', '피부과']).first()
                elif pkg_data['package_type'] == 'dental':
                    dept = departments.filter(name_ko='치과').first()
                else:
                    dept = departments.filter(name_ko='내과').first()
                
                pkg_data['department'] = dept or departments.first()
                MedicalPackage.objects.get_or_create(**pkg_data)

    def create_users(self, count):
        """사용자 생성"""
        self.stdout.write(f'{count}명의 사용자 데이터를 생성합니다...')
        
        countries = ['KR', 'CN', 'JP', 'US', 'RU', 'SA', 'DE', 'FR', 'GB']
        languages = ['ko', 'en', 'zh', 'ja', 'ru', 'ar', 'de', 'fr']
        
        korean_names = [
            ('김', '민수'), ('이', '지영'), ('박', '철수'), ('최', '영희'), ('정', '준호'),
            ('강', '수진'), ('조', '현우'), ('윤', '미영'), ('장', '성민'), ('임', '하늘'),
            ('한', '예진'), ('오', '태윤'), ('서', '은지'), ('권', '동현'), ('황', '소라')
        ]
        
        foreign_names = [
            ('Wang', 'Lei'), ('Li', 'Mei'), ('Zhang', 'Wei'), ('Chen', 'Yu'),
            ('Tanaka', 'Hiroshi'), ('Sato', 'Yuki'), ('Suzuki', 'Akiko'),
            ('Smith', 'John'), ('Johnson', 'Emily'), ('Brown', 'Michael'),
            ('Petrov', 'Ivan'), ('Ivanov', 'Anna'), ('Sidorov', 'Dmitri'),
            ('Al-Rashid', 'Ahmed'), ('Al-Zahra', 'Fatima')
        ]
        
        for i in range(count):
            country = random.choice(countries)
            
            if country == 'KR':
                last_name, first_name = random.choice(korean_names)
                username = f"{first_name.lower()}{random.randint(100, 999)}"
            else:
                last_name, first_name = random.choice(foreign_names)
                username = f"{first_name.lower()}{last_name.lower()}{random.randint(10, 99)}"
            
            # 사용자 생성
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password='testpass123',
                first_name=first_name,
                last_name=last_name,
                phone_number=f"+82-10-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                birth_date=datetime(
                    random.randint(1970, 2000), 
                    random.randint(1, 12), 
                    random.randint(1, 28)
                ).date(),
                country=country,
                preferred_language=random.choice(languages),
                passport_number=f"{country}{random.randint(100000, 999999)}",
                emergency_contact=f"응급연락처{i+1}",
                emergency_phone=f"+82-10-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            )
            
            # 가입일을 과거로 설정
            user.date_joined = timezone.now() - timedelta(days=random.randint(1, 365))
            user.save()

    def create_doctors(self, count):
        """의사 생성"""
        self.stdout.write(f'{count}명의 의사 데이터를 생성합니다...')
        
        departments = MedicalDepartment.objects.all()
        
        doctor_names = [
            '김대현', '이수진', '박영호', '최민아', '정우석',
            '강혜진', '조성호', '윤미래', '장동건', '임채은',
            '한지민', '오준영', '서현우', '권태영', '황수아'
        ]
        
        specializations = {
            '내과': ['당뇨병', '고혈압', '심장질환', '소화기질환', '호흡기질환'],
            '외과': ['복강경수술', '갑상선수술', '유방수술', '대장수술', '위수술'],
            '성형외과': ['코성형', '눈성형', '가슴성형', '지방흡입', '안면윤곽'],
            '피부과': ['여드름치료', '레이저시술', '보톡스', '필러', '미백관리'],
            '치과': ['임플란트', '교정', '심미치료', '치주치료', '구강외과'],
            '안과': ['백내장', '녹내장', '라식', '라섹', '망막질환'],
            '이비인후과': ['코수술', '중이염', '인후염', '수면무호흡', '알레르기'],
            '정형외과': ['관절염', '척추질환', '스포츠의학', '인공관절', '골절치료'],
            '산부인과': ['임신관리', '부인과질환', '불임치료', '갱년기관리', '산전관리'],
            '신경외과': ['뇌종양', '척추수술', '뇌혈관질환', '외상', '뇌전증']
        }
        
        languages_list = [
            '한국어, 영어', '한국어, 중국어', '한국어, 일본어', 
            '한국어, 영어, 중국어', '한국어, 러시아어',
            '한국어, 아랍어', '한국어, 영어, 일본어'
        ]
        
        for i in range(count):
            dept = random.choice(departments)
            name = random.choice(doctor_names)
            doctor_names.remove(name)  # 중복 방지
            
            spec_list = specializations.get(dept.name_ko, ['일반진료'])
            specialization = random.choice(spec_list)
            
            Doctor.objects.create(
                name=name,
                department=dept,
                specialization=specialization,
                experience_years=random.randint(5, 30),
                languages=random.choice(languages_list),
                bio=f"{name} 원장은 {dept.name_ko} 분야의 전문의로, {specialization} 치료에 특화되어 있습니다. "
                    f"풍부한 임상경험을 바탕으로 환자 중심의 맞춤 치료를 제공합니다.",
                consultation_fee=Decimal(random.randint(80, 300)) * 1000,
                is_available=random.choice([True, True, True, False]),  # 75% 확률로 진료 가능
                rating=round(random.uniform(4.0, 5.0), 1)
            )

    def create_doctor_schedules(self):
        """의사 스케줄 생성"""
        self.stdout.write('의사 스케줄 데이터를 생성합니다...')
        
        doctors = Doctor.objects.all()
        
        for doctor in doctors:
            # 평일 스케줄 (월-금)
            for weekday in range(5):
                if random.choice([True, True, True, False]):  # 75% 확률로 근무
                    DoctorSchedule.objects.create(
                        doctor=doctor,
                        weekday=weekday,
                        start_time='09:00',
                        end_time='18:00',
                        is_available=True
                    )
            
            # 토요일 스케줄 (50% 확률)
            if random.choice([True, False]):
                DoctorSchedule.objects.create(
                    doctor=doctor,
                    weekday=5,
                    start_time='09:00',
                    end_time='13:00',
                    is_available=True
                )

    def create_appointments(self, count):
        """예약 생성"""
        self.stdout.write(f'{count}개의 예약 데이터를 생성합니다...')
        
        users = User.objects.filter(is_superuser=False)
        doctors = Doctor.objects.filter(is_available=True)
        packages = MedicalPackage.objects.all()
        
        statuses = ['pending', 'confirmed', 'completed', 'cancelled']
        payment_statuses = ['pending', 'paid', 'failed', 'refunded']
        
        symptoms_list = [
            '두통이 자주 발생합니다', '복통이 있습니다', '감기 증상이 있습니다',
            '피부 트러블이 있습니다', '치아가 아픕니다', '무릎이 아픕니다',
            '시야가 흐릿합니다', '목이 아픕니다', '어깨가 결립니다',
            '소화가 잘 안됩니다'
        ]
        
        for i in range(count):
            user = random.choice(users)
            doctor = random.choice(doctors)
            
            # 날짜 설정 (과거 30일 ~ 미래 60일)
            appointment_date = timezone.now() + timedelta(
                days=random.randint(-30, 60),
                hours=random.randint(9, 17),
                minutes=random.choice([0, 30])
            )
            
            # 패키지 선택 (30% 확률)
            package = random.choice(packages) if random.random() < 0.3 else None
            
            # 총 금액 계산
            total_amount = doctor.consultation_fee
            if package:
                total_amount += package.price
            
            status = random.choice(statuses)
            payment_status = random.choice(payment_statuses)
            
            # 과거 예약은 완료 상태로
            if appointment_date < timezone.now():
                status = 'completed'
                payment_status = 'paid'
            
            appointment = Appointment.objects.create(
                patient=user,
                doctor=doctor,
                package=package,
                appointment_date=appointment_date,
                status=status,
                payment_status=payment_status,
                total_amount=total_amount,
                symptoms=random.choice(symptoms_list),
                medical_history=f"과거 병력 {i+1}",
                allergies="특이사항 없음" if random.random() > 0.3 else "약물 알레르기",
                medications="복용 약물 없음" if random.random() > 0.2 else "고혈압약 복용중",
                notes=f"기타 사항 {i+1}"
            )
            
            # 결제 정보 생성 (결제 완료된 경우)
            if payment_status == 'paid':
                Payment.objects.create(
                    appointment=appointment,
                    amount=total_amount,
                    currency='KRW',
                    payment_method=random.choice(['credit_card', 'bank_transfer', 'paypal']),
                    transaction_id=f"TXN{random.randint(100000, 999999)}"
                )

    def create_reviews(self):
        """후기 생성"""
        self.stdout.write('후기 데이터를 생성합니다...')
        
        completed_appointments = Appointment.objects.filter(status='completed')
        
        review_titles = [
            '정말 만족스러운 진료였습니다',
            '친절하고 전문적인 상담',
            '기대 이상의 결과',
            '다시 방문하고 싶습니다',
            '추천하고 싶은 병원',
            '전문적인 치료에 감사합니다',
            '정확한 진단과 치료',
            '세심한 배려에 감동',
            '최고의 의료 서비스',
            '신뢰할 수 있는 의료진'
        ]
        
        review_contents = [
            "의료진이 매우 친절하고 전문적이었습니다. 설명도 자세히 해주셔서 안심이 되었습니다.",
            "시설이 깔끔하고 대기시간도 짧았습니다. 치료 결과도 매우 만족스럽습니다.",
            "해외에서 왔는데 통역 서비스와 픽업 서비스가 정말 도움이 되었습니다.",
            "정확한 진단과 적절한 치료로 빠르게 회복할 수 있었습니다.",
            "의료진의 전문성과 병원 시설 모두 최고 수준이었습니다.",
            "사후 관리까지 꼼꼼하게 해주셔서 정말 감사했습니다.",
            "예약부터 진료까지 모든 과정이 체계적이고 효율적이었습니다.",
            "언어 소통에 대한 걱정이 있었는데 전혀 문제없이 진료받을 수 있었습니다."
        ]
        
        # 완료된 예약의 50%에 대해 후기 생성
        for appointment in random.sample(list(completed_appointments), 
                                       min(len(completed_appointments) // 2, len(completed_appointments))):
            Review.objects.create(
                appointment=appointment,
                rating=random.randint(4, 5),  # 4-5점 위주로
                title=random.choice(review_titles),
                content=random.choice(review_contents),
                recommend=random.choice([True, True, True, False])  # 75% 추천
            )

    def create_notifications(self):
        """알림 생성"""
        self.stdout.write('알림 데이터를 생성합니다...')
        
        users = User.objects.filter(is_superuser=False)
        
        notification_data = [
            {
                'title': '예약이 확정되었습니다',
                'message': '진료 예약이 성공적으로 확정되었습니다. 예약 시간에 맞춰 내원해 주세요.',
                'notification_type': 'appointment'
            },
            {
                'title': '결제가 완료되었습니다',
                'message': '진료비 결제가 정상적으로 처리되었습니다.',
                'notification_type': 'payment'
            },
            {
                'title': '진료 하루 전 알림',
                'message': '내일 예정된 진료가 있습니다. 시간에 맞춰 내원해 주세요.',
                'notification_type': 'reminder'
            },
            {
                'title': '새로운 의료 패키지 출시',
                'message': '맞춤형 건강검진 패키지가 새롭게 출시되었습니다.',
                'notification_type': 'system'
            },
            {
                'title': '진료 후기 작성 요청',
                'message': '받으신 진료에 대한 소중한 후기를 남겨주세요.',
                'notification_type': 'system'
            }
        ]
        
        for user in users:
            # 각 사용자마다 1-5개의 알림 생성
            for _ in range(random.randint(1, 5)):
                notif_data = random.choice(notification_data)
                Notification.objects.create(
                    user=user,
                    title=notif_data['title'],
                    message=notif_data['message'],
                    notification_type=notif_data['notification_type'],
                    is_read=random.choice([True, False]),
                    created_at=timezone.now() - timedelta(days=random.randint(0, 30))
                )