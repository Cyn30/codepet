"""GitHub Device Flow and operating-system credential storage."""

from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .build_config import PUBLIC_GITHUB_CLIENT_ID

try:
    import keyring
    from keyring.errors import KeyringError
except ImportError:  # pragma: no cover - desktop extra installs keyring
    keyring = None
    KeyringError = Exception

DEVICE_CODE_URL = "https://github.com/login/device/code"
ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
KEYRING_SERVICE = "CodePet GitHub"
KEYRING_ACCOUNT = "user-access-token"
DEVICE_GRANT = "urn:ietf:params:oauth:grant-type:device_code"


class AuthenticationError(RuntimeError):
    pass


@dataclass(frozen=True)
class DeviceAuthorization:
    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int


@dataclass
class Credential:
    access_token: str
    refresh_token: str | None = None
    expires_at: str | None = None

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        expiry = datetime.fromisoformat(self.expires_at)
        return datetime.now(timezone.utc) >= expiry - timedelta(minutes=2)


_session_credential: Credential | None = None


def configured_client_id() -> str:
    return os.environ.get("CODEPET_GITHUB_CLIENT_ID", PUBLIC_GITHUB_CLIENT_ID).strip()


def begin_device_flow(client_id: str | None = None) -> DeviceAuthorization:
    resolved_client_id = client_id or configured_client_id()
    if not resolved_client_id:
        raise AuthenticationError(
            "This build has no GitHub App Client ID. See the maintainer setup guide."
        )
    result = _post_form(DEVICE_CODE_URL, {"client_id": resolved_client_id})
    try:
        return DeviceAuthorization(
            device_code=result["device_code"],
            user_code=result["user_code"],
            verification_uri=result["verification_uri"],
            expires_in=int(result["expires_in"]),
            interval=max(5, int(result.get("interval", 5))),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise AuthenticationError("GitHub returned an invalid device authorization") from exc


def complete_device_flow(
    authorization: DeviceAuthorization,
    client_id: str | None = None,
) -> Credential:
    resolved_client_id = client_id or configured_client_id()
    deadline = time.monotonic() + authorization.expires_in
    interval = authorization.interval
    while time.monotonic() < deadline:
        time.sleep(interval)
        result = _post_form(
            ACCESS_TOKEN_URL,
            {
                "client_id": resolved_client_id,
                "device_code": authorization.device_code,
                "grant_type": DEVICE_GRANT,
            },
        )
        error = result.get("error")
        if not error:
            credential = _credential_from_response(result)
            save_credential(credential)
            return credential
        if error == "authorization_pending":
            continue
        if error == "slow_down":
            interval += 5
            continue
        messages = {
            "access_denied": "GitHub authorization was cancelled",
            "expired_token": "The GitHub device code expired",
            "incorrect_device_code": "GitHub rejected the device code",
        }
        raise AuthenticationError(messages.get(error, result.get("error_description", error)))
    raise AuthenticationError("The GitHub device code expired")


def resolve_token() -> str:
    environment_token = os.environ.get("GITHUB_TOKEN", "").strip()
    if environment_token:
        return environment_token

    credential = load_credential()
    if credential:
        if credential.is_expired:
            credential = refresh_credential(credential)
        return credential.access_token

    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.SubprocessError) as exc:
        raise AuthenticationError(
            "Connect GitHub in CodePet Home, run 'gh auth login', or set GITHUB_TOKEN"
        ) from exc
    token = result.stdout.strip()
    if not token:
        raise AuthenticationError("GitHub CLI did not return an access token")
    return token


def refresh_credential(credential: Credential) -> Credential:
    client_id = configured_client_id()
    if not client_id or not credential.refresh_token:
        delete_credential()
        raise AuthenticationError("GitHub authorization expired. Connect GitHub again.")
    result = _post_form(
        ACCESS_TOKEN_URL,
        {
            "client_id": client_id,
            "grant_type": "refresh_token",
            "refresh_token": credential.refresh_token,
        },
    )
    if result.get("error"):
        delete_credential()
        raise AuthenticationError("GitHub authorization expired. Connect GitHub again.")
    refreshed = _credential_from_response(result)
    save_credential(refreshed)
    return refreshed


def save_credential(credential: Credential) -> None:
    global _session_credential
    _session_credential = credential
    if keyring is None:
        return
    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_ACCOUNT, json.dumps(asdict(credential)))
    except KeyringError:
        return


def load_credential() -> Credential | None:
    if _session_credential:
        return _session_credential
    if keyring is None:
        return None
    try:
        raw = keyring.get_password(KEYRING_SERVICE, KEYRING_ACCOUNT)
        return Credential(**json.loads(raw)) if raw else None
    except (KeyringError, TypeError, ValueError, json.JSONDecodeError):
        return None


def delete_credential() -> None:
    global _session_credential
    _session_credential = None
    if keyring is None:
        return
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_ACCOUNT)
    except KeyringError:
        return


def _credential_from_response(result: dict) -> Credential:
    token = str(result.get("access_token", "")).strip()
    if not token:
        raise AuthenticationError("GitHub did not return an access token")
    expires_at = None
    if result.get("expires_in"):
        expires_at = (
            datetime.now(timezone.utc) + timedelta(seconds=int(result["expires_in"]))
        ).isoformat()
    return Credential(token, result.get("refresh_token"), expires_at)


def _post_form(url: str, values: dict[str, str]) -> dict:
    request = Request(
        url,
        data=urlencode(values).encode("utf-8"),
        headers={"Accept": "application/json", "User-Agent": "CodePet/0.4"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            return json.load(response)
    except HTTPError as exc:
        raise AuthenticationError(f"GitHub authentication returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise AuthenticationError(f"Unable to reach GitHub authentication: {exc}") from exc
