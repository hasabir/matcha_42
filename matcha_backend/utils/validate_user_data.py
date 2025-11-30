import re
import logging

logger = logging.getLogger(__name__)

# Try to import dns.resolver, but make it optional
try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    logger.warning("dnspython not available - DNS validation will be skipped")

def validate_email_format(email):
    """
    Validate email format using regex
    Returns (is_valid, error_message)
    """
    if not email or not email.strip():
        return False, "Email is required"
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    # Check for common typos
    parts = email.split('@')
    if len(parts) != 2:
        return False, "Invalid email format"
    
    local_part, domain = parts
    
    # Validate local part
    if not local_part or len(local_part) > 64:
        return False, "Invalid email format"
    
    # Validate domain part
    if not domain or len(domain) > 255:
        return False, "Invalid email format"
    
    # Check if domain has at least one dot
    if '.' not in domain:
        return False, "Invalid email domain"
    
    return True, None

def validate_email_domain(email):
    """
    Validate that the email domain has valid MX records
    Returns (is_valid, error_message)
    """
    # If DNS module not available, skip DNS validation
    if not DNS_AVAILABLE:
        logger.debug("DNS validation skipped - dnspython not installed")
        return True, None
    
    try:
        domain = email.split('@')[1]
        
        # Try to get MX records
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if not mx_records:
                return False, "Email domain does not exist or cannot receive emails"
            return True, None
        except dns.resolver.NXDOMAIN:
            return False, "Email domain does not exist"
        except dns.resolver.NoAnswer:
            # No MX records, try A record as fallback
            try:
                dns.resolver.resolve(domain, 'A')
                return True, None
            except:
                return False, "Email domain does not exist or cannot receive emails"
        except dns.resolver.NoNameservers:
            return False, "Email domain cannot be verified"
        except Exception as e:
            logger.warning(f"DNS lookup failed for {domain}: {e}")
            # Don't block registration if DNS lookup fails due to network issues
            # Just warn and allow it through
            return True, None
            
    except Exception as e:
        logger.error(f"Error validating email domain: {e}")
        # Don't block registration on validation errors
        return True, None

def validate_email(email):
    """
    Complete email validation: format + domain
    Returns (is_valid, error_message)
    """
    # First check format
    is_valid_format, format_error = validate_email_format(email)
    if not is_valid_format:
        return False, format_error
    
    # Then check domain
    is_valid_domain, domain_error = validate_email_domain(email)
    if not is_valid_domain:
        return False, domain_error
    
    return True, None

def validate_user_data(user_data):
    required_fields = ["username", "email", "password", "first_name", "last_name"]
    for field in required_fields:
        if field not in user_data or not user_data[field]:
            return False
    return True