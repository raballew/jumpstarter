import shutil
from unittest.mock import patch

from .session import SessionMetadata
from .utils import launch_shell


def test_launch_shell(tmp_path, monkeypatch):
    monkeypatch.setenv("SHELL", shutil.which("true"))
    exit_code = launch_shell(
        host=str(tmp_path / "test.sock"), context="remote", allow=["*"], unsafe=False, use_profiles=False
    )
    assert exit_code == 0

    monkeypatch.setenv("SHELL", shutil.which("false"))
    exit_code = launch_shell(
        host=str(tmp_path / "test.sock"), context="remote", allow=["*"], unsafe=False, use_profiles=False
    )
    assert exit_code == 1


def test_launch_shell_prints_motd_for_interactive_shell(tmp_path, monkeypatch):
    monkeypatch.setenv("SHELL", shutil.which("true"))
    session_metadata = SessionMetadata(exporter_name="my-board")
    with patch("jumpstarter.common.utils._print_motd") as mock_print:
        launch_shell(
            host=str(tmp_path / "test.sock"),
            context="my-board",
            allow=["*"],
            unsafe=False,
            use_profiles=False,
            session_metadata=session_metadata,
        )
    mock_print.assert_called_once_with(session_metadata)


def test_launch_shell_no_motd_when_command_provided(tmp_path, monkeypatch):
    monkeypatch.setenv("SHELL", shutil.which("true"))
    session_metadata = SessionMetadata(exporter_name="my-board")
    with patch("jumpstarter.common.utils._print_motd") as mock_print:
        launch_shell(
            host=str(tmp_path / "test.sock"),
            context="my-board",
            allow=["*"],
            unsafe=False,
            use_profiles=False,
            command=(shutil.which("true"),),
            session_metadata=session_metadata,
        )
    mock_print.assert_not_called()


def test_print_motd_shows_exporter_name(capsys):
    from .utils import _print_motd

    session_metadata = SessionMetadata(exporter_name="laptop-test-exporter")
    _print_motd(session_metadata)
    captured = capsys.readouterr()
    assert "Connected to exporter: laptop-test-exporter" in captured.out


def test_launch_shell_command_output_not_polluted(tmp_path, monkeypatch):
    monkeypatch.setenv("SHELL", shutil.which("true"))
    session_metadata = SessionMetadata(
        exporter_name="my-board",
        motd="Welcome to the board",
    )
    with patch("jumpstarter.common.utils._print_motd") as mock_print:
        launch_shell(
            host=str(tmp_path / "test.sock"),
            context="my-board",
            allow=["*"],
            unsafe=False,
            use_profiles=False,
            command=(shutil.which("true"),),
            session_metadata=session_metadata,
        )
    mock_print.assert_not_called()


def test_print_motd_shows_custom_motd_text(capsys):
    from .utils import _print_motd

    session_metadata = SessionMetadata(
        exporter_name="my-board",
        motd="Welcome to the test board\nPlease be careful",
    )
    _print_motd(session_metadata)
    captured = capsys.readouterr()
    assert "Connected to exporter: my-board" in captured.out
    assert "Welcome to the test board\nPlease be careful" in captured.out


def test_print_motd_multiline(capsys):
    from .utils import _print_motd

    session_metadata = SessionMetadata(
        exporter_name="my-board",
        motd="Line 1\nLine 2\nLine 3",
    )
    _print_motd(session_metadata)
    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert lines[0] == "Connected to exporter: my-board"
    assert lines[1] == "Line 1"
    assert lines[2] == "Line 2"
    assert lines[3] == "Line 3"


def test_print_motd_no_custom_text_when_motd_is_none(capsys):
    from .utils import _print_motd

    session_metadata = SessionMetadata(exporter_name="my-board", motd=None)
    _print_motd(session_metadata)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Connected to exporter: my-board"


def test_print_motd_very_long_message(capsys):
    from .utils import _print_motd

    long_text = "x" * 10001
    session_metadata = SessionMetadata(exporter_name="my-board", motd=long_text)
    _print_motd(session_metadata)
    captured = capsys.readouterr()
    assert long_text in captured.out


def test_print_motd_special_characters(capsys):
    from .utils import _print_motd

    special_text = "tab:\there\nunicode: \u00e9\u00e8\u00ea\nansi: \x1b[31mred\x1b[0m"
    session_metadata = SessionMetadata(exporter_name="my-board", motd=special_text)
    _print_motd(session_metadata)
    captured = capsys.readouterr()
    assert special_text in captured.out


def test_launch_shell_no_motd_when_no_session_metadata(tmp_path, monkeypatch):
    monkeypatch.setenv("SHELL", shutil.which("true"))
    with patch("jumpstarter.common.utils._print_motd") as mock_print:
        launch_shell(
            host=str(tmp_path / "test.sock"),
            context="remote",
            allow=["*"],
            unsafe=False,
            use_profiles=False,
        )
    mock_print.assert_not_called()
