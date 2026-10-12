# SOS Desktop

A Linux desktop front-end for the [sos](https://github.com/sosreport/sos) suite of tools.
Generate, view, obfuscate, and upload sos reports without leaving the GUI.

SOS Desktop is part of the sos ecosystem and follows the same conventions and
coding standards as the sos project itself. Contributions are welcome; see the
[Contributing](#contributing) section below.

---

## Features

- **Generate Report**: runs `sos report --batch` elevated via `pkexec`
- **Upload Selected**:  runs `sos upload` on the selected archive
- **Generate Remote Report**: runs `sos report` on a remote host over SSH
- **Multi-node Collect**: runs `sos collect` with a configuration dialog (nodes, cluster type, SSH options, transport)
- **Obfuscate Report**: runs `sos clean` on the selected archive to replace IPs, MACs, hostnames, and custom keywords
- **Authorize System**: runs `sos upload --preauth` to store an auth token without uploading a file (requires sos with `--preauth` support)
- **Live output panel**: non-blocking subprocess output streamed in real time
- **SOS Reports tab**: lists archives found in `/var/tmp`, with name, date, size, and path; right-click to open file, open folder, or copy path
- **Dark theme**: Fusion dark palette with a dark red accent colour
- **Persistent settings**: Case ID, Upload Target, and other options saved via `QSettings`

---

## Requirements

### Runtime

| Requirement | Notes |
|---|---|
| Python 3.11+ | |
| PyQt6 >= 6.6 | |
| `sos` | Provides `sos report`, `sos upload`, `sos collect`, `sos clean` |
| `pkexec` + polkit agent | Required for privilege elevation; a graphical polkit agent must be running |
| `xdg-open` or `gio` | For opening files and folders |
| `ssh` | Only for Generate Remote Report |

### Optional

| Requirement | Notes |
|---|---|
| `oc` (OpenShift CLI) | Only needed if using Multi-node Collect with `oc` transport |

---

## Installation

### End users: pipx (recommended)

[pipx](https://pypa.github.io/pipx/) installs the app into an isolated environment and
exposes the `sos-desktop` command system-wide:

```bash
pipx install .
sos-desktop
```

### End users: pip into a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
sos-desktop
```

---

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"   # editable install + linting tools

sos-desktop               # launch the app
```

Code changes take effect immediately with an editable install.

### Linting

The project uses **pylint** and **flake8**, configured to match the sos project's
own standards (`pylintrc` is kept in sync with sos). Max line length is 79.

```bash
tox                    # runs flake8 and pylint
tox -e flake8          # flake8 only
tox -e pylint          # pylint only
```

Please make sure both pass (pylint score 10.00/10, flake8 clean) before
submitting a patch.

---

## Contributing

Contributions of all sizes are welcome: bug fixes, new featrues, and
documentation improvements.

**Before opening a pull request:**

- Run `tox` and ensure pylint and flake8 pass cleanly.
- Keep new string literals in `constants.py` rather than inline.
- New sos command options should be wired through `SosActions`, not scattered
  elsewhere.
- If you are adding a new `QSettings` key, add it to `SettingsKeys` in
  `constants.py` and document what it persists.
- Credential fields (passwords, secret keys) must not be written to `QSettings`.

---

## License

GPL-2.0-or-later. See `LICENSE`.

By contributing to this project you agree that your contributions will be
licensed under the same terms.
