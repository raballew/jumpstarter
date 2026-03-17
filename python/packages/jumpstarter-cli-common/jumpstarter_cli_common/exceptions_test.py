import logging
import os
import socket
import ssl

import pytest

from jumpstarter_cli_common.exceptions import (
    ClickExceptionRed,
    async_handle_exceptions,
    friendly_error_message,
    handle_exceptions,
    handle_exceptions_with_reauthentication,
    is_debug_mode,
)


class TestIsDebugMode:
    def test_returns_false_by_default(self):
        os.environ.pop("JUMPSTARTER_DEBUG", None)
        assert is_debug_mode() is False

    def test_returns_true_when_env_var_set(self, monkeypatch):
        monkeypatch.setenv("JUMPSTARTER_DEBUG", "1")
        assert is_debug_mode() is True

    def test_returns_false_when_env_var_empty(self, monkeypatch):
        monkeypatch.setenv("JUMPSTARTER_DEBUG", "")
        assert is_debug_mode() is False

    def test_returns_true_when_root_logger_is_debug(self):
        os.environ.pop("JUMPSTARTER_DEBUG", None)
        logger = logging.getLogger()
        original_level = logger.level
        try:
            logger.setLevel(logging.DEBUG)
            assert is_debug_mode() is True
        finally:
            logger.setLevel(original_level)


class TestFriendlyErrorMessage:
    def test_returns_none_for_unknown_exception(self):
        assert friendly_error_message(ValueError("something")) is None

    def test_ssl_certificate_verify_failed(self):
        exc = ssl.SSLCertVerificationError("certificate verify failed")
        msg = friendly_error_message(exc)
        assert msg is not None
        assert "TLS" in msg or "certificate" in msg.lower()

    def test_ssl_error(self):
        exc = ssl.SSLError("SSL handshake failed")
        msg = friendly_error_message(exc)
        assert msg is not None
        assert "TLS" in msg or "SSL" in msg

    def test_connection_refused(self):
        exc = ConnectionRefusedError("Connection refused")
        msg = friendly_error_message(exc)
        assert msg is not None
        assert "refused" in msg.lower() or "connect" in msg.lower()

    def test_os_error_connection_refused(self):
        exc = OSError(111, "Connection refused")
        msg = friendly_error_message(exc)
        assert msg is not None

    def test_timeout_error(self):
        exc = TimeoutError("timed out")
        msg = friendly_error_message(exc)
        assert msg is not None
        assert "timed out" in msg.lower() or "timeout" in msg.lower()

    def test_dns_resolution_failure(self):
        exc = socket.gaierror(8, "Name or service not known")
        msg = friendly_error_message(exc)
        assert msg is not None
        assert "resolve" in msg.lower() or "DNS" in msg or "hostname" in msg.lower()


class TestHandleExceptionsWithFriendlyMessages:
    def test_ssl_error_shows_friendly_message(self, monkeypatch):
        monkeypatch.delenv("JUMPSTARTER_DEBUG", raising=False)
        logging.getLogger().setLevel(logging.WARNING)

        @handle_exceptions
        def raises_ssl():
            raise ssl.SSLCertVerificationError("certificate verify failed")

        with pytest.raises(ClickExceptionRed) as exc_info:
            raises_ssl()
        assert "TLS" in str(exc_info.value.message)

    def test_connection_refused_shows_friendly_message(self, monkeypatch):
        monkeypatch.delenv("JUMPSTARTER_DEBUG", raising=False)
        logging.getLogger().setLevel(logging.WARNING)

        @handle_exceptions
        def raises_refused():
            raise ConnectionRefusedError("Connection refused")

        with pytest.raises(ClickExceptionRed) as exc_info:
            raises_refused()
        assert "refused" in str(exc_info.value.message).lower()

    def test_timeout_shows_friendly_message(self, monkeypatch):
        monkeypatch.delenv("JUMPSTARTER_DEBUG", raising=False)
        logging.getLogger().setLevel(logging.WARNING)

        @handle_exceptions
        def raises_timeout():
            raise TimeoutError("connection timed out")

        with pytest.raises(ClickExceptionRed) as exc_info:
            raises_timeout()
        assert "timed out" in str(exc_info.value.message).lower()

    def test_dns_error_shows_friendly_message(self, monkeypatch):
        monkeypatch.delenv("JUMPSTARTER_DEBUG", raising=False)
        logging.getLogger().setLevel(logging.WARNING)

        @handle_exceptions
        def raises_dns():
            raise socket.gaierror(8, "Name or service not known")

        with pytest.raises(ClickExceptionRed) as exc_info:
            raises_dns()
        assert "resolve" in str(exc_info.value.message).lower() or "hostname" in str(exc_info.value.message).lower()

    def test_debug_mode_reraises_original_exception(self, monkeypatch):
        monkeypatch.setenv("JUMPSTARTER_DEBUG", "1")

        @handle_exceptions
        def raises_ssl():
            raise ssl.SSLCertVerificationError("certificate verify failed")

        with pytest.raises(ssl.SSLCertVerificationError):
            raises_ssl()

    def test_unknown_exception_reraises(self, monkeypatch):
        monkeypatch.delenv("JUMPSTARTER_DEBUG", raising=False)
        logging.getLogger().setLevel(logging.WARNING)

        @handle_exceptions
        def raises_value_error():
            raise ValueError("something else")

        with pytest.raises(ValueError):
            raises_value_error()


class TestAsyncHandleExceptionsWithFriendlyMessages:
    @pytest.mark.asyncio(loop_scope="function")
    async def test_ssl_error_shows_friendly_message(self, monkeypatch):
        monkeypatch.delenv("JUMPSTARTER_DEBUG", raising=False)
        logging.getLogger().setLevel(logging.WARNING)

        @async_handle_exceptions
        async def raises_ssl():
            raise ssl.SSLCertVerificationError("certificate verify failed")

        with pytest.raises(ClickExceptionRed) as exc_info:
            await raises_ssl()
        assert "TLS" in str(exc_info.value.message)

    @pytest.mark.asyncio(loop_scope="function")
    async def test_debug_mode_reraises_original(self, monkeypatch):
        monkeypatch.setenv("JUMPSTARTER_DEBUG", "1")

        @async_handle_exceptions
        async def raises_ssl():
            raise ssl.SSLCertVerificationError("certificate verify failed")

        with pytest.raises(ssl.SSLCertVerificationError):
            await raises_ssl()


class TestHandleExceptionsWithReauthFriendlyMessages:
    def test_ssl_error_shows_friendly_message(self, monkeypatch):
        monkeypatch.delenv("JUMPSTARTER_DEBUG", raising=False)
        logging.getLogger().setLevel(logging.WARNING)

        def dummy_login(config):
            pass

        @handle_exceptions_with_reauthentication(dummy_login)
        def raises_ssl():
            raise ssl.SSLCertVerificationError("certificate verify failed")

        with pytest.raises(ClickExceptionRed) as exc_info:
            raises_ssl()
        assert "TLS" in str(exc_info.value.message)

    def test_debug_mode_reraises_original(self, monkeypatch):
        monkeypatch.setenv("JUMPSTARTER_DEBUG", "1")

        def dummy_login(config):
            pass

        @handle_exceptions_with_reauthentication(dummy_login)
        def raises_ssl():
            raise ssl.SSLCertVerificationError("certificate verify failed")

        with pytest.raises(ssl.SSLCertVerificationError):
            raises_ssl()
