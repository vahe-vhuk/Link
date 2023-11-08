import re
from datetime import datetime


def is_valid_url(url):
    url_pattern = re.compile(r'^(https?|ftp)://[^\s/$.?#].[^\s]*$')
    if re.match(url_pattern, url):
        return True
    else:
        return False


def is_expired_date(date: list[int]):
    now = datetime.now()
    if date[0] < now.year:
        return False
    if date[1] < now.month:
        return False
    if date[2] < now.day:
        return False
    return True
