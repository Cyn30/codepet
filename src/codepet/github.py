"""Authenticated, read-only GitHub GraphQL client."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .auth import AuthenticationError, resolve_token
from .rewards import ActivityEvent

API_URL = "https://api.github.com/graphql"
QUERY = """
query CodePetActivity($since: GitTimestamp!, $from: DateTime!) {
  viewer {
    id
    login
    repositories(first: 50, affiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER],
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 50, since: $since) {
                nodes { oid author { user { id } } }
              }
            }
          }
        }
      }
    }
    contributionsCollection(from: $from) {
      pullRequestContributions(first: 50) {
        nodes { pullRequest { id } }
      }
      repositoryContributions(first: 50) {
        nodes { repository { id } }
      }
    }
  }
}
"""


class GitHubError(AuthenticationError):
    pass


def fetch_recent_activity(
    since: str, token: str | None = None
) -> tuple[str, list[ActivityEvent]]:
    try:
        resolved_token = token or resolve_token()
    except AuthenticationError as exc:
        raise GitHubError(str(exc)) from exc
    payload = json.dumps(
        {"query": QUERY, "variables": {"since": since, "from": since}}
    ).encode()
    request = Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {resolved_token}",
            "Content-Type": "application/json",
            "User-Agent": "CodePet/0.4",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            result = json.load(response)
    except HTTPError as exc:
        raise GitHubError(f"GitHub returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise GitHubError(f"Unable to reach GitHub: {exc}") from exc

    if result.get("errors"):
        raise GitHubError(result["errors"][0].get("message", "GitHub query failed"))

    viewer = result["data"]["viewer"]
    events = _parse_events(viewer)
    return viewer["login"], events


def _parse_events(viewer: dict) -> list[ActivityEvent]:
    events: list[ActivityEvent] = []
    viewer_id = viewer["id"]
    for repository in viewer["repositories"]["nodes"]:
        branch = repository.get("defaultBranchRef")
        if not branch:
            continue
        for commit in branch["target"]["history"]["nodes"]:
            user = (commit.get("author") or {}).get("user")
            if user and user.get("id") == viewer_id:
                events.append(ActivityEvent(f"commit:{commit['oid']}", "commit"))

    contributions = viewer["contributionsCollection"]
    for node in contributions["pullRequestContributions"]["nodes"]:
        events.append(ActivityEvent(f"pull_request:{node['pullRequest']['id']}", "pull_request"))
    for node in contributions["repositoryContributions"]["nodes"]:
        events.append(ActivityEvent(f"repository:{node['repository']['id']}", "repository"))
    return events
