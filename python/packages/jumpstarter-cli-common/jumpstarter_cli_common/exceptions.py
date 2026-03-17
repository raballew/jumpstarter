import logging
import os
import socket
import ssl
import types
from functools import wraps
from types import TracebackType
from typing import NoReturn

import click

from jumpstarter.common.exceptions import ConnectionError, JumpstarterException

ERRNO_CONNECTION_REFUSED = 111


def is_debug_mode() -> bool:
    debug_env = os.environ.get("JUMPSTARTER_DEBUG", "")
    if debug_env:
        return True
    root_logger = logging.getLogger()
    return root_logger.level == logging.DEBUG


def friendly_error_message(exc: BaseException) -> str | None:
    if isinstance(exc, ssl.SSLCertVerificationError):
        return (
            "TLS certificate verification failed. "
            "Check that the server certificate is valid or use --insecure-tls-config for testing."
        )
    if isinstance(exc, ssl.SSLError):
        return f"TLS/SSL error: {exc}. Check your TLS configuration."
    if isinstance(exc, ConnectionRefusedError):
        return "Connection refused. Is the server running and reachable?"
    if isinstance(exc, OSError) and getattr(exc, "errno", None) == ERRNO_CONNECTION_REFUSED:
        return "Connection refused. Is the server running and reachable?"
    if isinstance(exc, socket.gaierror):
        return f"Could not resolve hostname. Check the server address and your DNS settings. ({exc})"
    if isinstance(exc, TimeoutError):
        return "Connection timed out. Check the server address and your network connection."
    return None


class ClickExceptionRed(click.ClickException):
    def format_message(self) -> str:
        return click.style(self.message, fg="red")


def _raise_friendly_or_reraise(exc: BaseException) -> None:
    if is_debug_mode():
        raise exc
    msg = friendly_error_message(exc)
    if msg:
        raise ClickExceptionRed(msg) from None
    raise exc


def async_handle_exceptions(func):
    """Decorator to handle exceptions in async functions, including those wrapped in BaseExceptionGroup."""

    @wraps(func)
    async def wrapped(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BaseExceptionGroup as eg:
            for exc in leaf_exceptions(eg, fix_tracebacks=False):
                if isinstance(exc, JumpstarterException):
                    raise ClickExceptionRed(str(exc)) from None
                elif isinstance(exc, click.ClickException):
                    raise exc from None
                else:
                    _raise_friendly_or_reraise(exc)
            raise eg
        except JumpstarterException as e:
            raise ClickExceptionRed(str(e)) from None
        except click.ClickException:
            raise
        except Exception as e:
            _raise_friendly_or_reraise(e)

    return wrapped


def handle_exceptions(func):
    """Decorator to handle exceptions in blocking functions."""

    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except JumpstarterException as e:
            raise ClickExceptionRed(str(e)) from None
        except click.ClickException:
            raise
        except Exception as e:
            _raise_friendly_or_reraise(e)

    return wrapped


def _handle_connection_error_with_reauth(exc, login_func):
    """Handle ConnectionError with reauthentication logic."""
    if "expired" in str(exc).lower():
        click.echo(click.style("Token is expired, triggering re-authentication", fg="red"))
        config = exc.get_config()
        login_func(config)
        raise ClickExceptionRed("Please try again now") from None
    else:
        raise ClickExceptionRed(str(exc)) from None


def _handle_single_exception_with_reauth(exc, login_func):
    """Handle a single exception (may raise)."""
    if isinstance(exc, ConnectionError):
        _handle_connection_error_with_reauth(exc, login_func)
    elif isinstance(exc, JumpstarterException):
        raise ClickExceptionRed(str(exc)) from None
    elif isinstance(exc, click.ClickException):
        raise exc from None
    # Not handled: fall through


def _handle_exception_group_with_reauth(eg, login_func) -> NoReturn:
    """Handle exceptions wrapped in BaseExceptionGroup."""
    for exc in leaf_exceptions(eg, fix_tracebacks=False):
        _handle_single_exception_with_reauth(exc, login_func)
    # If no handled exceptions, re-raise the original group
    raise eg


def handle_exceptions_with_reauthentication(login_func):
    """Decorator to handle exceptions in blocking functions, including those wrapped in BaseExceptionGroup."""

    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BaseExceptionGroup as eg:
                _handle_exception_group_with_reauth(eg, login_func)
            except (ConnectionError, JumpstarterException, click.ClickException) as e:
                _handle_single_exception_with_reauth(e, login_func)
            except Exception as e:
                _raise_friendly_or_reraise(e)

        return wrapped

    return decorator


def find_exception_in_group(
    eg: BaseExceptionGroup, exc_type: type[BaseException], *, fix_tracebacks: bool = False
) -> BaseException | None:
    """
    Find the first exception of a specific type in an ExceptionGroup.

    Args:
        eg: The ExceptionGroup to search
        exc_type: The exception type to find
        fix_tracebacks: Whether to fix tracebacks in leaf exceptions

    Returns:
        The first matching exception, or None if not found
    """
    for exc in leaf_exceptions(eg, fix_tracebacks=fix_tracebacks):
        if isinstance(exc, exc_type):
            return exc
    return None


# https://peps.python.org/pep-0654/
def leaf_exceptions(self: BaseExceptionGroup, *, fix_tracebacks: bool = True) -> list[BaseException]:
    """
    Return a flat list of all 'leaf' exceptions.

    If fix_tracebacks is True, each leaf will have the traceback replaced
    with a composite so that frames attached to intermediate groups are
    still visible when debugging. Pass fix_tracebacks=False to disable
    this modification, e.g. if you expect to raise the group unchanged.
    """

    def _flatten(group: BaseExceptionGroup, parent_tb: TracebackType | None = None):
        group_tb = group.__traceback__
        combined_tb = _combine_tracebacks(parent_tb, group_tb)
        result = []
        for exc in group.exceptions:
            if isinstance(exc, BaseExceptionGroup):
                result.extend(_flatten(exc, combined_tb))
            elif fix_tracebacks:
                tb = _combine_tracebacks(combined_tb, exc.__traceback__)
                result.append(exc.with_traceback(tb))
            else:
                result.append(exc)
        return result

    return _flatten(self)


def _combine_tracebacks(
    tb1: TracebackType | None,
    tb2: TracebackType | None,
) -> TracebackType | None:
    """
    Combine two tracebacks, putting tb1 frames before tb2 frames.

    If either is None, return the other.
    """
    if tb1 is None:
        return tb2
    if tb2 is None:
        return tb1

    # Convert tb1 to a list of frames
    frames = []
    current = tb1
    while current is not None:
        frames.append((current.tb_frame, current.tb_lasti, current.tb_lineno))
        current = current.tb_next

    # Create a new traceback starting with tb2
    new_tb = tb2

    # Add frames from tb1 to the beginning (in reverse order)
    for frame, lasti, lineno in reversed(frames):
        new_tb = types.TracebackType(tb_next=new_tb, tb_frame=frame, tb_lasti=lasti, tb_lineno=lineno)

    return new_tb
