import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException


class TestMainEndpoints:
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Autopilot.dev Backend" in response.json()["message"]

    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    @patch('main.trigger_workflow')
    @patch('main.get_user_collection')
    def test_trigger_autopilot_success(self, mock_get_users, mock_trigger, client, mock_db):
        """Test successful autopilot trigger."""
        # Mock user lookup
        mock_user = {"email": "test@example.com", "github_token": "token"}
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = mock_user
        mock_get_users.return_value = mock_collection

        # Mock workflow trigger
        mock_trigger.return_value = {"id": "exec_123", "state": {"startDate": "2024-01-01"}}

        payload = {
            "repo_url": "https://github.com/test/repo",
            "branch": "main",
            "user_email": "test@example.com"
        }

        response = client.post("/api/trigger", json=payload)
        assert response.status_code == 200
        assert "execution_id" in response.json()

    def test_trigger_autopilot_missing_user(self, client, mock_db):
        """Test trigger with missing user."""
        with patch('main.get_user_collection') as mock_get_users:
            mock_collection = AsyncMock()
            mock_collection.find_one.return_value = None
            mock_get_users.return_value = mock_collection

            payload = {
                "repo_url": "https://github.com/test/repo",
                "branch": "main",
                "user_email": "nonexistent@example.com"
            }

            response = client.post("/api/trigger", json=payload)
            assert response.status_code == 404

    @patch('main.get_logs_stream')
    def test_stream_status_success(self, mock_stream, client):
        """Test successful status streaming."""
        mock_stream.return_value = ["log line 1", "log line 2"]

        response = client.get("/api/status/test_execution")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"

    def test_stream_status_failure(self, client):
        """Test status streaming failure."""
        with patch('main.get_logs_stream', side_effect=Exception("Stream error")):
            response = client.get("/api/status/test_execution")
            assert response.status_code == 500

    def test_get_runs_success(self, client, mock_db):
        """Test successful runs retrieval."""
        # Mock the database query
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [
            {"_id": "id1", "repo": "repo1", "status": "COMPLETED"},
            {"_id": "id2", "repo": "repo2", "status": "RUNNING"}
        ]
        mock_db.runs.find.return_value.sort.return_value.limit.return_value = mock_cursor

        response = client.get("/api/runs")
        assert response.status_code == 200
        assert "runs" in response.json()

    @patch('main.process_kestra_completion')
    def test_kestra_webhook_success(self, mock_process, client, mock_db):
        """Test successful Kestra webhook."""
        payload = {"id": "exec_123", "executionId": "exec_123"}

        response = client.post("/webhook/kestra", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "processed"

    def test_kestra_webhook_missing_id(self, client):
        """Test Kestra webhook with missing execution ID."""
        payload = {}

        response = client.post("/webhook/kestra", json=payload)
        assert response.status_code == 500

    def test_get_video_success(self, client, mock_db):
        """Test successful video retrieval."""
        # Mock artefact lookup
        mock_artefact = {"video_bytes": b'test_video_data'}
        mock_db.artefacts.find_one.return_value = mock_artefact

        response = client.get("/api/video/test_execution")
        assert response.status_code == 200
        assert response.headers["content-type"] == "video/mp4"

    def test_get_video_not_found(self, client, mock_db):
        """Test video retrieval when artefact not found."""
        mock_db.artefacts.find_one.return_value = None

        response = client.get("/api/video/test_execution")
        assert response.status_code == 404

    @patch('main.get_coderabbit_insights')
    @patch('main.generate_together_report')
    def test_generate_together_report_success(self, mock_report, mock_insights, client):
        """Test successful Together AI report generation."""
        mock_insights.return_value = {"insights": "data"}
        mock_report.return_value = "Generated report"

        payload = {
            "repo_url": "https://github.com/test/repo",
            "execution_id": "exec_123",
            "user_email": "test@example.com"
        }

        response = client.post("/api/together-ai/generate", json=payload)
        assert response.status_code == 200
        assert "report" in response.json()

    def test_generate_together_report_missing_repo(self, client):
        """Test Together AI report generation with missing repo URL."""
        payload = {"execution_id": "exec_123"}

        response = client.post("/api/together-ai/generate", json=payload)
        assert response.status_code == 400

    def test_get_together_report_success(self, client, mock_db):
        """Test successful Together AI report retrieval."""
        mock_report = {
            "execution_id": "exec_123",
            "report": "Test report",
            "created_at": MagicMock()
        }
        mock_report["created_at"].isoformat.return_value = "2024-01-01T00:00:00"
        mock_db.together_reports.find_one.return_value = mock_report

        response = client.get("/api/together-ai/report/exec_123")
        assert response.status_code == 200
        assert response.json()["report"] == "Test report"

    def test_get_together_report_not_found(self, client, mock_db):
        """Test Together AI report retrieval when not found."""
        mock_db.together_reports.find_one.return_value = None

        response = client.get("/api/together-ai/report/exec_123")
        assert response.status_code == 404

    @patch('main.subprocess.run')
    def test_trigger_cline_success(self, mock_subprocess, client, mock_db):
        """Test successful Cline agent trigger."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_subprocess.return_value = mock_result

        payload = {
            "repo_url": "https://github.com/test/repo",
            "branch": "main",
            "bug_report": "Test bug",
            "github_token": "token"
        }

        response = client.post("/api/cline/trigger", json=payload)
        assert response.status_code == 200
        assert "execution_id" in response.json()

    def test_trigger_cline_missing_repo(self, client):
        """Test Cline trigger with missing repo URL."""
        payload = {"branch": "main"}

        response = client.post("/api/cline/trigger", json=payload)
        assert response.status_code == 400

    def test_get_cline_status_success(self, client, mock_db):
        """Test successful Cline status retrieval."""
        mock_cline_doc = {
            "execution_id": "cline_123",
            "status": "completed",
            "output": "Test output",
            "created_at": MagicMock(),
            "completed_at": MagicMock()
        }
        mock_cline_doc["created_at"].isoformat.return_value = "2024-01-01T00:00:00"
        mock_cline_doc["completed_at"].isoformat.return_value = "2024-01-01T01:00:00"
        mock_db.cline_executions.find_one.return_value = mock_cline_doc

        response = client.get("/api/cline/status/cline_123")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_get_cline_status_not_found(self, client, mock_db):
        """Test Cline status retrieval when not found."""
        mock_db.cline_executions.find_one.return_value = None

        response = client.get("/api/cline/status/cline_123")
        assert response.status_code == 404

    def test_vercel_webhook_success(self, client):
        """Test successful Vercel webhook."""
        payload = {"deployed": True}

        response = client.post("/webhook/vercel", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "deployed"
