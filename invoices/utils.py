"""
Utility functions for the invoices app.
"""
import re


def normalize_phone_number(phone):
    """
    Normalize phone number to E.164 format.
    
    Args:
        phone: Phone number string
        
    Returns:
        Normalized phone number in E.164 format
    """
    if not phone:
        return ''
    
    # Remove all non-digit characters except +
    phone = re.sub(r'[^\d+]', '', phone)
    
    # Already in E.164 format
    if phone.startswith('+'):
        return phone
    
    # International format with 00
    elif phone.startswith('00'):
        return '+' + phone[2:]
    
    # US/Canada 10-digit number
    elif len(phone) == 10:
        return '+1' + phone
    
    # US/Canada 11-digit starting with 1
    elif len(phone) == 11 and phone.startswith('1'):
        return '+' + phone
    
    # Default: add + prefix
    else:
        return '+' + phone


def format_whatsapp_number(phone):
    """
    Format phone number for WhatsApp API (includes whatsapp: prefix).
    
    Args:
        phone: Phone number string
        
    Returns:
        WhatsApp-formatted phone number
    """
    normalized = normalize_phone_number(phone)
    if not normalized.startswith('whatsapp:'):
        return f'whatsapp:{normalized}'
    return normalized
