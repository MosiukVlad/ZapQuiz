from django import template
from datetime import timedelta

register = template.Library()


@register.filter()
def duration_hm(value):
    """Format a timedelta or seconds as H:MM (hours:minutes).
    If value is None, return an empty string.
    """
    if value is None:
        return ''

    # Accept timedelta or numeric seconds
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
    else:
        try:
            total_seconds = int(value)
        except Exception:
            return ''

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}:{minutes:02d}"


@register.filter()
def duration_seconds(value):
    """Return total seconds as integer for a timedelta or numeric input.
    """
    if value is None:
        return 0
    if isinstance(value, timedelta):
        return int(value.total_seconds())
    try:
        return int(value)
    except Exception:
        return 0
