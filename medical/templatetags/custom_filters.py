# medical_tourism/templatetags/__init__.py
# 빈 파일로 생성

# medical_tourism/templatetags/custom_filters.py
from django import template
from django.utils.timesince import timesince
from datetime import datetime
import re

register = template.Library()

@register.filter
def split(value, arg):
    """문자열을 분할하는 필터"""
    return value.split(arg)

@register.filter
def first_word(value):
    """첫 번째 단어만 반환"""
    if value:
        return str(value).split()[0]
    return value

@register.filter
def days_since_joined(date_joined):
    """가입일로부터 경과 일수 계산"""
    if date_joined:
        delta = datetime.now().date() - date_joined.date()
        return delta.days
    return 0

@register.filter
def get_item(dictionary, key):
    """딕셔너리에서 키로 값 가져오기"""
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    """곱셈 필터"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """나눗셈 필터"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def currency(value):
    """통화 형식으로 포맷"""
    try:
        return f"₩{int(float(value)):,}"
    except (ValueError, TypeError):
        return value

@register.filter
def star_rating(value):
    """별점을 HTML로 변환"""
    try:
        rating = float(value)
        full_stars = int(rating)
        half_star = rating - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        
        html = '<span class="star-rating">'
        html += '<i class="fas fa-star text-yellow-400"></i>' * full_stars
        if half_star:
            html += '<i class="fas fa-star-half-alt text-yellow-400"></i>'
        html += '<i class="far fa-star text-gray-300"></i>' * empty_stars
        html += '</span>'
        return html
    except (ValueError, TypeError):
        return ''

@register.filter
def format_phone(value):
    """전화번호 포맷팅"""
    if value:
        # Remove all non-digits
        digits = re.sub(r'\D', '', str(value))
        if len(digits) == 11 and digits.startswith('010'):
            return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        elif len(digits) >= 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return value

@register.filter
def truncate_chars(value, length):
    """문자 수 제한"""
    if len(str(value)) > length:
        return str(value)[:length] + '...'
    return value

@register.filter
def get_language_name(code):
    """언어 코드를 언어명으로 변환"""
    languages = {
        'ko': '한국어',
        'en': 'English',
        'zh': '中文',
        'ja': '日本語',
        'ru': 'Русский',
        'ar': 'العربية',
        'de': 'Deutsch',
        'fr': 'Français',
    }
    return languages.get(code, code)

@register.filter
def get_country_flag(country_code):
    """국가 코드를 깃발 이모지로 변환"""
    flags = {
        'KR': '🇰🇷',
        'US': '🇺🇸',
        'CN': '🇨🇳',
        'JP': '🇯🇵',
        'RU': '🇷🇺',
        'SA': '🇸🇦',
        'DE': '🇩🇪',
        'FR': '🇫🇷',
        'GB': '🇬🇧',
    }
    return flags.get(country_code, '🌍')

@register.simple_tag
def get_setting(name, default=None):
    """설정값 가져오기"""
    from django.conf import settings
    return getattr(settings, name, default)

@register.inclusion_tag('medical_tourism/components/rating_stars.html')
def rating_stars(rating, size='md'):
    """별점 컴포넌트"""
    return {
        'rating': float(rating) if rating else 0,
        'size': size,
        'full_stars': int(float(rating)) if rating else 0,
        'empty_stars': 5 - (int(float(rating)) if rating else 0),
    }

@register.inclusion_tag('medical_tourism/components/status_badge.html')
def status_badge(status, status_choices):
    """상태 배지 컴포넌트"""
    status_colors = {
        'pending': 'yellow',
        'confirmed': 'green',
        'cancelled': 'red',
        'completed': 'blue',
        'paid': 'green',
        'failed': 'red',
        'refunded': 'gray',
    }
    
    return {
        'status': status,
        'status_display': dict(status_choices).get(status, status),
        'color': status_colors.get(status, 'gray'),
    }