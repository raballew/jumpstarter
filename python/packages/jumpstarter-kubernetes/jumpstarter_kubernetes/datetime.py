import re
from datetime import datetime, timedelta, timezone


def _parse_duration(duration_str: str) -> timedelta:
    match = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", duration_str)
    if not match or not any(match.groups()):
        return timedelta()
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def time_remaining(begin_time: str | None, duration: str | None) -> str:
    if begin_time is None or duration is None:
        return "-"
    begin = datetime.strptime(begin_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    end = begin + _parse_duration(duration)
    remaining = end - now
    total_seconds = remaining.total_seconds()
    if total_seconds <= 0:
        return "Expired"
    if total_seconds < 60:
        return "<1m"
    total_minutes = int(total_seconds // 60)
    if total_minutes < 60:
        return f"{total_minutes}m"
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if minutes > 0:
        return f"{hours}h {minutes}m"
    return f"{hours}h"


def time_since(t_str: str):
    t = datetime.strptime(t_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    elapsed = now - t

    if elapsed.total_seconds() < 60:
        return f"{int(elapsed.total_seconds())}s"
    elif elapsed.total_seconds() < 3600:
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        return f"{minutes}m{seconds}s" if seconds > 0 else f"{minutes}m"
    elif elapsed.total_seconds() < 86400:
        hours = int(elapsed.total_seconds() // 3600)
        minutes = int((elapsed.total_seconds() % 3600) // 60)
        return f"{hours}h{minutes}m" if minutes > 0 and hours < 2 else f"{hours}h"
    elif elapsed.total_seconds() < 2592000:
        days = elapsed.days
        hours = int((elapsed.total_seconds() % 86400) // 3600)
        return f"{days}d{hours}h" if hours > 0 else f"{days}d"
    elif elapsed.total_seconds() < 31536000:
        months = int(elapsed.days / 30)
        days = elapsed.days % 30
        return f"{months}mo{days}d" if days > 0 else f"{months}mo"
    else:
        years = int(elapsed.days / 365)
        months = int((elapsed.days % 365) / 30)
        return f"{years}y{months}mo" if months > 0 else f"{years}y"
