import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from codepet.auth import (
    AuthenticationError,
    Credential,
    DeviceAuthorization,
    begin_device_flow,
    complete_device_flow,
)


class AuthenticationTests(unittest.TestCase):
    @patch("codepet.auth._post_form")
    def test_device_flow_parses_github_response(self, post_form):
        post_form.return_value = {
            "device_code": "device",
            "user_code": "ABCD-EFGH",
            "verification_uri": "https://github.com/login/device",
            "expires_in": 900,
            "interval": 5,
        }
        authorization = begin_device_flow("client-id")
        self.assertEqual(authorization.user_code, "ABCD-EFGH")
        post_form.assert_called_once()

    @patch("codepet.auth.save_credential")
    @patch("codepet.auth.time.sleep")
    @patch("codepet.auth._post_form")
    def test_device_flow_waits_until_user_authorizes(self, post_form, sleep, save):
        post_form.side_effect = [
            {"error": "authorization_pending"},
            {"access_token": "token", "expires_in": 28800, "refresh_token": "refresh"},
        ]
        authorization = DeviceAuthorization("device", "CODE", "https://example.com", 900, 5)
        credential = complete_device_flow(authorization, "client-id")
        self.assertEqual(credential.access_token, "token")
        self.assertEqual(post_form.call_count, 2)
        self.assertEqual(sleep.call_count, 2)
        save.assert_called_once_with(credential)

    @patch("codepet.auth._post_form")
    def test_access_denied_is_reported(self, post_form):
        post_form.return_value = {"error": "access_denied"}
        authorization = DeviceAuthorization("device", "CODE", "https://example.com", 900, 5)
        with patch("codepet.auth.time.sleep"), self.assertRaisesRegex(
            AuthenticationError, "cancelled"
        ):
            complete_device_flow(authorization, "client-id")

    def test_expiring_credential_uses_safety_window(self):
        credential = Credential(
            "token",
            expires_at=(datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat(),
        )
        self.assertTrue(credential.is_expired)


if __name__ == "__main__":
    unittest.main()
