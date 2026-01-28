import re

def clean_domain(domain):
    domain = domain.strip()
    domain = re.sub(r'^https?://', '', domain)
    domain = re.sub(r'^(\*\.|\*|www\.)+', '', domain)
    domain = domain.split('/')[0]
    domain = domain.split(':')[0]
    if domain.endswith('.'):
        domain = domain[:-1]
    domain = domain.split('?')[0]
    domain = domain.split('#')[0]
    
    return domain.strip().lower()