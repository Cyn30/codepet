# Security Policy

Please report credential exposure or other security issues privately through GitHub's security advisory feature. Do not open a public Issue containing a token or private repository information.

CodePet does not store GitHub credentials. It reads `GITHUB_TOKEN` from the process environment or asks GitHub CLI for a token only while performing a sync.
