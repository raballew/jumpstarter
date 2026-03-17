from .session import SessionMetadata


def test_session_metadata_motd_defaults_to_none():
    metadata = SessionMetadata(exporter_name="test-board")
    assert metadata.motd is None
    assert metadata.exporter_name == "test-board"


def test_session_metadata_motd_stores_value():
    metadata = SessionMetadata(exporter_name="test-board", motd="Welcome")
    assert metadata.motd == "Welcome"
