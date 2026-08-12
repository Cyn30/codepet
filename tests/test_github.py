import unittest

from codepet.github import _parse_events


class GitHubParsingTests(unittest.TestCase):
    def test_parser_filters_commits_to_authenticated_user(self):
        viewer = {
            "id": "viewer-1",
            "login": "octocat",
            "repositories": {"nodes": [
                {"defaultBranchRef": {"target": {"history": {"nodes": [
                    {"oid": "mine", "author": {"user": {"id": "viewer-1"}}},
                    {"oid": "theirs", "author": {"user": {"id": "viewer-2"}}},
                ]}}}},
                {"defaultBranchRef": None},
            ]},
            "contributionsCollection": {
                "pullRequestContributions": {"nodes": [{"pullRequest": {"id": "pr-1"}}]},
                "repositoryContributions": {"nodes": [{"repository": {"id": "repo-1"}}]},
            },
        }
        events = _parse_events(viewer)
        self.assertEqual(
            [(event.id, event.kind) for event in events],
            [
                ("commit:mine", "commit"),
                ("pull_request:pr-1", "pull_request"),
                ("repository:repo-1", "repository"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
