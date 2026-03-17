from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from .datetime import time_remaining, time_since


def test_time_since_seconds():
    now = datetime.now(timezone.utc)
    past = now - timedelta(seconds=30)
    t_str = past.strftime("%Y-%m-%dT%H:%M:%SZ")
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        mock_datetime.strptime.return_value = past.replace(tzinfo=None)
        result = time_since(t_str)
        assert result == "30s"


def test_time_since_minutes_with_seconds():
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=5, seconds=30)
    t_str = past.strftime("%Y-%m-%dT%H:%M:%SZ")
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        mock_datetime.strptime.return_value = past.replace(tzinfo=None)
        result = time_since(t_str)
        assert result == "5m30s"


def test_time_since_minutes_without_seconds():
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=10)
    t_str = past.strftime("%Y-%m-%dT%H:%M:%SZ")
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        mock_datetime.strptime.return_value = past.replace(tzinfo=None)
        result = time_since(t_str)
        assert result == "10m"


def test_time_since_hours_with_minutes_under_2h():
    now = datetime.now(timezone.utc)
    past = now - timedelta(hours=1, minutes=30)
    t_str = past.strftime("%Y-%m-%dT%H:%M:%SZ")
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        mock_datetime.strptime.return_value = past.replace(tzinfo=None)
        result = time_since(t_str)
        assert result == "1h30m"


def test_time_since_hours_without_minutes():
    now = datetime.now(timezone.utc)
    past = now - timedelta(hours=3, minutes=15)
    t_str = past.strftime("%Y-%m-%dT%H:%M:%SZ")
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        mock_datetime.strptime.return_value = past.replace(tzinfo=None)
        result = time_since(t_str)
        assert result == "3h"


def test_time_since_days_with_hours():
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=5, hours=6)
    t_str = past.strftime("%Y-%m-%dT%H:%M:%SZ")
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        mock_datetime.strptime.return_value = past.replace(tzinfo=None)
        result = time_since(t_str)
        assert result == "5d6h"


def test_time_since_days_without_hours():
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=10)
    t_str = past.strftime("%Y-%m-%dT%H:%M:%SZ")
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        mock_datetime.strptime.return_value = past.replace(tzinfo=None)
        result = time_since(t_str)
        assert result == "10d"


def test_time_since_months_with_days():
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=65)
    t_str = past.strftime("%Y-%m-%dT%H:%M:%SZ")
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        mock_datetime.strptime.return_value = past.replace(tzinfo=None)
        result = time_since(t_str)
        assert result == "2mo5d"


def test_time_since_months_without_days():
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=90)
    t_str = past.strftime("%Y-%m-%dT%H:%M:%SZ")
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        mock_datetime.strptime.return_value = past.replace(tzinfo=None)
        result = time_since(t_str)
        assert result == "3mo"


def test_time_since_years_with_months():
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=425)
    t_str = past.strftime("%Y-%m-%dT%H:%M:%SZ")
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        mock_datetime.strptime.return_value = past.replace(tzinfo=None)
        result = time_since(t_str)
        assert result == "1y2mo"


def test_time_since_years_without_months():
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=730)
    t_str = past.strftime("%Y-%m-%dT%H:%M:%SZ")
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        mock_datetime.strptime.return_value = past.replace(tzinfo=None)
        result = time_since(t_str)
        assert result == "2y"


def test_time_remaining_hours_and_minutes():
    now = datetime(2021, 10, 1, 0, 30, 0, tzinfo=timezone.utc)
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_dt:
        mock_dt.now.return_value = now
        mock_dt.strptime.return_value = datetime(2021, 10, 1, 0, 0, 0)
        result = time_remaining("2021-10-01T00:00:00Z", "3h")
    assert result == "2h 30m"


def test_time_remaining_minutes_only():
    now = datetime(2021, 10, 1, 0, 15, 0, tzinfo=timezone.utc)
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_dt:
        mock_dt.now.return_value = now
        mock_dt.strptime.return_value = datetime(2021, 10, 1, 0, 0, 0)
        result = time_remaining("2021-10-01T00:00:00Z", "1h")
    assert result == "45m"


def test_time_remaining_less_than_one_minute():
    now = datetime(2021, 10, 1, 0, 59, 30, tzinfo=timezone.utc)
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_dt:
        mock_dt.now.return_value = now
        mock_dt.strptime.return_value = datetime(2021, 10, 1, 0, 0, 0)
        result = time_remaining("2021-10-01T00:00:00Z", "1h")
    assert result == "<1m"


def test_time_remaining_expired():
    now = datetime(2021, 10, 1, 2, 0, 0, tzinfo=timezone.utc)
    with patch("jumpstarter_kubernetes.datetime.datetime") as mock_dt:
        mock_dt.now.return_value = now
        mock_dt.strptime.return_value = datetime(2021, 10, 1, 0, 0, 0)
        result = time_remaining("2021-10-01T00:00:00Z", "1h")
    assert result == "Expired"


def test_time_remaining_no_begin_time():
    result = time_remaining(None, "1h")
    assert result == "-"


def test_time_remaining_no_duration():
    result = time_remaining("2021-10-01T00:00:00Z", None)
    assert result == "-"
