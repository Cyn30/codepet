# CodePet

**Keep coding. Raise a friend.**

CodePet is an open-source desktop companion for macOS, Windows, and Linux. It lives in a transparent window, rests below the macOS menu bar, walks along the screen, reacts to care with emoji mood bubbles, and grows from real GitHub activity. CodePet never monitors your keyboard or reads your source code.

**Read this guide in Chinese:** [README.zh-CN.md](README.zh-CN.md)

> Public alpha: the gameplay, desktop overlay, two-pet household, shop, GitHub rewards, save migration, and release build pipeline are implemented. Published installers should still be tested on every supported operating system before a stable release.

## What it feels like

CodePet uses the same desktop-application pattern as interactive companions such as Bongo Cat: a frameless, transparent, always-on-top native window plus a system tray/menu bar controller. The artwork and gameplay are original. CodePet uses 2D pixel sprites rather than Live2D, which keeps animation readable, lightweight, and easy for contributors to extend.

## Features

- Transparent, draggable desktop pets with no rectangular background
- Six breed-specific production atlases with eight-frame idle, walk, run, eat, affection, and sleep clips
- Species-aware behavior scheduling with bounded phases, recent-state memory, and no random teleporting
- Loop-boundary animation blending, gradual acceleration, braking, and a post-meal rest period
- White emoji thought bubbles that communicate mood and needs
- Cats and dogs with six original breed skins
- One household with up to two pets
- Increasing XP requirements at every level
- Five bond ranks from New Friends to Soulmates
- Hunger, happiness, energy, lifespan, streak, and offline time decay
- A household wallet, food inventory, and desktop shop
- Species-aware food preferences with positive and negative bond effects
- GitHub commit, pull request, and new-repository rewards
- Deterministic rewards and event deduplication
- Local-only save data; no telemetry or keyboard monitoring
- One-click GitHub Device Flow login with OS keychain storage
- GitHub CLI and environment-token fallbacks for developers

## Install a release

Prebuilt releases let users run CodePet without installing Python.

### macOS

1. Open the repository's **Releases** page.
2. Download `CodePet-macOS.dmg`.
3. Open the downloaded disk image.
4. Drag `CodePet.app` into **Applications**.
5. Open CodePet from Applications.

If an unsigned alpha build is blocked, right-click CodePet in Applications, select **Open**, then confirm **Open**. For a public stable release, maintainers should sign and notarize the app with an Apple Developer ID rather than asking users to bypass Gatekeeper.

### Windows

1. Open the repository's **Releases** page.
2. Download `CodePet-Windows.zip`.
3. Extract the entire zip file.
4. Open the extracted `CodePet` folder.
5. Run `CodePet.exe`.

Do not move only the `.exe`; the adjacent Qt libraries are part of the application.

### Linux

1. Download `CodePet-Linux.tar.gz` from **Releases**.
2. Extract it.
3. Run `CodePet/CodePet`.

Wayland behavior depends on the compositor. X11 currently offers the most consistent always-on-top transparent-window behavior.

## Run from source

Use Python 3.10 or later:

```bash
git clone https://github.com/Cyn30/codepet.git
cd codepet
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[desktop]"
codepet-desktop
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\activate
```

## First launch

1. Enter a name.
2. Choose cat or dog.
3. Choose a breed.
4. Set a lifespan between 14 and 3,650 days.
5. Select **Adopt**.
6. Use the CodePet Home window for pet selection, play, food, and the shop.
7. Right-click a desktop pet to rest, walk, run, resume natural behavior, return to the cage, sync GitHub, or hide the household.
8. Click a desktop pet to pet it and gain 1-2 bond points.

You may adopt a second pet from the Home window. GitHub rewards go to the currently selected pet, while coins and food belong to the shared household. This prevents one GitHub event from being rewarded twice.

## Natural animation behavior

CodePet does not choose a new pose independently on every timer tick. Each cat or dog
follows a bounded behavior phase: it may watch quietly, walk, run briefly, slow down,
or curl up for a longer rest. A short memory lowers the chance of returning to the
same recent activity, and no phase can continue forever. Cats favor longer naps and
shorter bursts; dogs favor longer walks.

Movement uses elapsed real time rather than a fixed number of pixels per frame. Walks
are about 10-16 pixels per second and runs about 27-38 pixels per second, so a few
steps cannot carry a pet across the desktop. Speed changes gradually. At a screen edge,
the pet brakes, pauses, then turns. Feeding always leads into rest and blocks running
for a digestion period. Visual clips change only after the current eight-frame loop
finishes, which prevents mid-pose cuts.

## Connect your private GitHub account

CodePet uses GitHub's read-only GraphQL API only when you choose **Sync GitHub**.
The desktop process can call this API directly over HTTPS; being a local transparent
window does not prevent network access. Your credential remains on your computer.

### Option A: Connect GitHub in the app (recommended for releases)

1. Open **CodePet Home**.
2. Select **Connect GitHub**.
3. CodePet copies a one-time code and opens GitHub in your browser.
4. Enter the code and approve the read-only GitHub App access.
5. Return to CodePet and select **Sync GitHub**.

CodePet uses GitHub's Device Flow. It stores the resulting user token in macOS
Keychain, Windows Credential Locker, or the Linux desktop keyring. The token is
never stored in `save.json`, the website, or the repository. The public Client ID
identifies the app and is safe to distribute; a Client Secret must never be bundled
inside a desktop application.

### Option B: GitHub CLI

1. Install [GitHub CLI](https://cli.github.com/).
2. Run:

   ```bash
   gh auth login
   ```

3. Select `GitHub.com`.
4. Select HTTPS.
5. Complete browser authentication.
6. Open CodePet Home and select **Sync GitHub**.

CodePet asks GitHub CLI for the current credential at sync time. It never writes that credential into the save file.

### Option C: fine-grained personal access token for development

1. Open GitHub **Settings > Developer settings > Personal access tokens > Fine-grained tokens**.
2. Select your account as resource owner.
3. Select only the repositories that CodePet should count.
4. Grant read-only repository access. Do not grant write or administration access.
5. Set a reasonable expiration date.
6. Start CodePet from a terminal containing the token:

   ```bash
   export GITHUB_TOKEN="github_pat_your_token_here"
   codepet-desktop
   ```

PowerShell:

```powershell
$env:GITHUB_TOKEN="github_pat_your_token_here"
codepet-desktop
```

Never paste a real token into this README, source code, Issues, screenshots, or commits. Revoke an exposed token immediately.

## Reward rules

Rewards are derived from a hash of the GitHub event ID. The same event always produces the same reward, and processed event IDs are retained so repeated synchronization cannot duplicate items.

| GitHub activity | XP | Coins | Bond | Food |
| --- | ---: | ---: | ---: | --- |
| Commit | 8-15 | 5-10 | 1-5 | 20% chance |
| Pull request | 12-20 | 5-10 | 2-5 | None |
| New repository | 5-8 | 1-3 | 1-2 | None |

The current API query reads recent commits from default branches in the first 50 recently pushed repositories and recent contribution records. Large accounts may need pagination in a future release.

## Food and shop balance

| Food | Price | Cat preference | Dog preference |
| --- | ---: | ---: | ---: |
| Cat Food | 15 | +3 to +5 | -2 to 0 |
| Dog Food | 15 | -2 to 0 | +3 to +5 |
| Chew Bone | 25 | -3 to 0 | +5 to +7 |
| Cooked Chicken | 35 | +4 to +7 | +4 to +7 |
| Salmon | 45 | +7 to +10 | +3 to +6 |
| Tuna | 60 | +9 to +13 | +1 to +4 |
| Celebration Feast | 100 | +10 to +14 | +10 to +14 |

Higher-priced universal food is safer for both species. Strongly species-specific food is cheaper but can reduce bond when given to the wrong pet. Food also restores hunger according to its catalog definition.

## Mood, care, and bond

The desktop bubble uses emoji rather than text so mood remains readable at a small size:

- `😊` or `🥰`: happy and well cared for
- `😴`: low energy
- `😟`: hungry or unhappy
- `😿` / `🥺`: urgent care threshold
- `💤`, `🏠`, `🌿`, and `✨`: activity feedback

Bond ranks are New Friends, Familiar, Friends, Best Friends, and Soulmates. Time decay is calculated in six-hour periods and capped, so a long absence cannot cause unbounded state changes in one launch. A very hungry pet can lose a limited amount of bond, but save data is never deleted.

## Build native installers

Installer builds must run on the target operating system; PyInstaller does not cross-compile.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[desktop,packaging]"
python scripts/build_desktop.py
```

Outputs:

- macOS: `dist/CodePet-macOS.dmg`
- Windows: `dist/CodePet-Windows.zip`
- Linux: `dist/CodePet-Linux.tar.gz`

The release workflow in `.github/workflows/release.yml` builds all three artifacts. Push a version tag such as `v0.4.0` to build them and attach them to a GitHub Release.

### What belongs on GitHub

| Item | Source repository | GitHub Release |
| --- | --- | --- |
| Extracted project source | Yes | GitHub generates a source archive automatically |
| macOS DMG | No | Yes, one versioned file |
| Windows ZIP / Linux TAR.GZ | No | Yes |
| Animation preview GIFs | Optional documentation only | No |
| Local output folders, caches, dependencies | No | No |

Do not commit installers or a source zip into the repository. Upload the
repository files themselves, and attach installers to a versioned Release.

### Maintainer: enable one-click GitHub login

This is a one-time publisher task; end users must not create their own Client ID.

1. Register a GitHub App under your organization or account.
2. Enable **Device Flow**.
3. Request only read access needed for activity counting: Metadata, Contents, and
   Pull requests. Do not request write or administration permissions.
4. Put the app's public Client ID in
   `src/codepet/build_config.py` as `PUBLIC_GITHUB_CLIENT_ID` before building a
   release. For local testing, set `CODEPET_GITHUB_CLIENT_ID` instead.
5. Never add a Client Secret to this repository or installer.

Without that public Client ID, **Connect GitHub** explains the missing maintainer
setup, while `gh auth login` and `GITHUB_TOKEN` remain available to developers.

## Production pixel animation pipeline

The runtime animation engine is state-based and independent from breed artwork.
Each breed uses an original 1024×768 transparent atlas: eight 128×128 frames for
each of idle, walking, running, eating, affection, and sleeping. Clip timing is
defined once in `animation.py`, and the loader rejects an incorrectly sized atlas
instead of silently displaying broken frames.

Use the exact contract in [assets/animations/README.md](assets/animations/README.md).
For a polished, non-generated look, redraw and onion-skin the frames in Aseprite,
check paw anchoring and silhouette consistency, and review the animation at runtime
speed. Other games may be used only as motion references; do not trace or copy their
sprites, palettes, silhouettes, or character designs.

All six initial breeds now have validated 1024×768 transparent atlases: 288 runtime
frames in total. The original still-pose sheet remains only as a defensive fallback
for a future breed whose atlas is missing. Run `scripts/validate_animation_atlas.py`
for structural validation and inspect the generated GIF previews before accepting an
art change.

## Development

```bash
python -m pip install -e ".[desktop,dev]"
python -m unittest discover -s tests -v
ruff check src tests scripts
```

Architecture:

```text
src/codepet/domain.py      household, pet, mood, bond, lifespan, time decay
src/codepet/catalog.py     food prices and species preferences
src/codepet/rewards.py     deterministic GitHub reward mapping
src/codepet/auth.py        GitHub Device Flow and OS credential storage
src/codepet/github.py      read-only GraphQL activity client
src/codepet/storage.py     atomic local persistence and migration
src/codepet/animation.py   reusable animation clips and state machine
src/codepet/sprites.py     validated breed-atlas loader and legacy fallback
src/codepet/overlay.py     transparent desktop pet windows
src/codepet/dashboard.py   household, adoption, inventory, and shop UI
src/codepet/desktop.py     application controller and tray integration
packaging/                 frozen application entry point and specification
scripts/                   cross-platform release build command
tests/                     domain, rewards, GitHub parsing, and storage tests
```

The UI calls domain operations but never calculates rewards, prices, or food preferences. This boundary is intentional: new pets, foods, or clients should reuse the existing rules instead of creating parallel implementations.

Create a clean repository-upload archive with:

```bash
python scripts/package_source.py outputs/CodePet-source.zip
```

The archive excludes virtual environments, website dependencies, build output,
test caches, nested Git data, and installer files. Extract it and upload its
contents to the repository root; do not commit the zip itself.

## Privacy

The default save file is `~/.codepet/save.json`. It contains pet state, inventory, coins, activity dates, and processed GitHub event IDs. It does not contain tokens, passwords, source code, commit messages, or repository contents.

CodePet does not monitor keyboard or mouse activity globally. Mouse interaction is handled only when the user clicks the visible pet or application window.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. All game-rule changes require tests. New artwork must be original and redistribution-compatible.

## License

Code is available under the [MIT License](LICENSE). See [ASSET-LICENSE.md](ASSET-LICENSE.md) for the original generated pixel-art assets.
