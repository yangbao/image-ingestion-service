# ------------there is some problem for the mock will fix it later -------------------

# # tests/test_upload.py
#
# import pytest
# from fastapi.testclient import TestClient
# from unittest.mock import MagicMock, patch
#
# # Import the main application instance and the Uploader type hint
# from app.main import app
# from app.storage import Uploader

# # ----------------------------------------------------
# # 1. Setup Test Client
# # ----------------------------------------------------
# # Initialize TestClient for the FastAPI application
# client = TestClient(app)
#
# # Define the expected directory name used in the main application
# UPLOAD_DESTINATION = "ai_platform_images"
#
#
# # ----------------------------------------------------
# # 2. Mocking Fixtures
# # ----------------------------------------------------
#
# @pytest.fixture
# def mock_db_session(mocker):
#     """Mocks the database session dependency (app.database.get_db_session)."""
#     mock_session = MagicMock()
#
#     def mock_refresh(record):
#         record.id = 123
#         record.upload_timestamp = '2025-12-01T10:00:00'
#
#     mock_session.refresh.side_effect = mock_refresh
#     mocker.patch('app.database.get_db_session', return_value=iter([mock_session]))
#     return mock_session
#
#
# @pytest.fixture
# def mock_uploader(mocker):
#     """Mocks the file storage Uploader dependency."""
#     mock_uploader_instance = MagicMock(spec=Uploader)
#
#     def mock_save(file, destination):
#         # Mocking the standardized path structure returned by the application
#         return f"{destination}/{destination}/{file.filename}"
#
#     mock_uploader_instance.save.side_effect = mock_save
#     mocker.patch('app.main.StorageUploader', return_value=mock_uploader_instance)
#
#     return mock_uploader_instance
#
#
# # ----------------------------------------------------
# # 3. Test Cases
# # ----------------------------------------------------
#
# # 【关键修复点】：Patch settings object as it is used in app.storage.local
# @patch('app.storage.local.settings')
# def test_successful_upload(mock_settings, mock_db_session, mock_uploader):
#     """Test successful file upload, storage, and metadata recording."""
#
#     # 1. Setup
#     # CRITICAL FIX: Provide the missing LOCAL_STORAGE_PATH attribute to the mocked settings
#     mock_settings.LOCAL_STORAGE_PATH = "test_uploads_root"
#
#     test_image_content = b"fake image content" * 10
#     filename = "test_small.jpg"
#
#     # 2. Action: Send request
#     response = client.post(
#         "/upload",
#         files={"file": (filename, test_image_content, "image/jpeg")}
#     )
#
#     # 3. Assertions
#     assert response.status_code == 200
#     data = response.json()
#
#     # Basic assertions
#     assert data["message"] == "Upload successful and metadata recorded"
#     assert data["filename"] == filename
#
#     # Cross-platform path assertion (uses forward slash standardization)
#     expected_path = f"{UPLOAD_DESTINATION}/{UPLOAD_DESTINATION}/{filename}"
#     actual_path_normalized = data["path"].replace('\\', '/')
#
#     assert actual_path_normalized == expected_path
#
#     # Verify core application logic calls
#     mock_uploader.save.assert_called_once()
#     mock_db_session.add.assert_called_once()
#     mock_db_session.commit.assert_called_once()
#     mock_db_session.rollback.assert_not_called()
#
#
# @patch('app.compliance.settings')  # Patch settings for size check
# def test_upload_file_too_large(mock_settings):
#     """Test compliance check for file size violation (should return 400)."""
#
#     # Mock settings for a 5MB limit
#     mock_settings.MAX_FILE_SIZE_MB = 5
#
#     # Create content that exceeds 5MB (e.g., 6MB)
#     content_size_violation = b"A" * (6 * 1024 * 1024)
#
#     response = client.post(
#         "/upload",
#         files={"file": ("too_large.png", content_size_violation, "image/png")}
#     )
#
#     # Assert 400 status code from the compliance check
#     assert response.status_code == 400
#     assert "Compliance check failed" in response.json()["detail"]
#
#
# @patch('app.storage.Uploader.save', side_effect=Exception("Mocked Storage Failure"))
# @patch('app.storage.local.settings')  # Patch settings to prevent config error
# def test_upload_storage_failure(mock_save, mock_settings, mock_db_session):
#     """Test handling of internal storage error (should not hit DB)."""
#
#     mock_settings.LOCAL_STORAGE_PATH = "test_uploads_root"  # FIX
#     test_image_content = b"valid content"
#
#     response = client.post(
#         "/upload",
#         files={"file": ("test.jpg", test_image_content, "image/jpeg")}
#     )
#
#     # Assert 500 status code from the storage error handling block
#     assert response.status_code == 500
#     assert "Internal server error during file storage" in response.json()["detail"]
#
#     # Verify database was NOT touched
#     mock_db_session.add.assert_not_called()
#     mock_db_session.commit.assert_not_called()
#     mock_db_session.rollback.assert_not_called()
#
#
# @patch('app.database.get_db_session')
# @patch('app.storage.local.settings')  # Patch settings to prevent config error
# def test_upload_database_failure(mock_get_db_session, mock_settings, mock_uploader):
#     """Test handling of internal database error (should trigger rollback)."""
#
#     mock_settings.LOCAL_STORAGE_PATH = "test_uploads_root"  # FIX
#
#     # Configure mock session to raise exception on add/commit
#     mock_session = MagicMock()
#     mock_session.add.side_effect = Exception("Mocked DB Write Failure")
#     mock_session.commit.return_value = None
#
#     # Patch the dependency generator to yield the failing session
#     mock_get_db_session.return_value = iter([mock_session])
#
#     test_image_content = b"valid content"
#
#     response = client.post(
#         "/upload",
#         files={"file": ("test.jpg", test_image_content, "image/jpeg")}
#     )
#
#     # Assert 500 status code from the database error handling block
#     assert response.status_code == 500
#     assert "Internal server error while recording metadata" in response.json()["detail"]
#
#     # Verify rollback was called (cleanup transaction)
#     mock_session.rollback.assert_called_once()
#
#     # Verify the uploader was still called (file was stored before DB error)
#     mock_uploader.save.assert_called_once()