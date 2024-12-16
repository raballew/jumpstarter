from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from jumpstarter.common.utils import serve

from .driver import HttpServer


@pytest.mark.asyncio
async def test_http_server():
    with TemporaryDirectory() as temp_dir:
        server = HttpServer(root_dir=temp_dir)
        await server.start()

        with serve(server) as client:
            test_content = b"test content"
            test_file_path = Path(temp_dir) / "test.txt"
            test_file_path.write_bytes(test_content)

            uploaded_filename = client.put_local_file(str(test_file_path))
            assert uploaded_filename == "test.txt"

            files = client.list_files()
            assert "test.txt" in files

            deleted_filename = client.delete_file("test.txt")
            assert deleted_filename == "test.txt"

            files_after_deletion = client.list_files()
            assert "test.txt" not in files_after_deletion

        await server.stop()
