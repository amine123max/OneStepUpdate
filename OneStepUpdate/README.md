# OneStepUpdate (GH Edition)

Desktop tool for logging into GitHub with `gh` and creating GitHub Releases from a simple Windows UI.

![OneStepUpdate](onestepupdate.png)

## What This Version Does

- Uses GitHub CLI for login with `gh auth login --web`
- Checks the current login with `gh api user`
- Loads repositories with `gh repo list`
- Creates a Release with `gh release create`
- Lets you attach local files as Release assets

## Requirements

- Windows 10/11
- Python 3
- [GitHub CLI (`gh`)](https://cli.github.com/) installed and available in `PATH`

## Project Files Kept For This GH Version

- `OneStepUpdate.py`: main GUI application
- `build_exe.bat`: local build script
- `requirements.txt`: Python dependencies
- `OneStepUpdate.ico`: app icon
- `onestepupdate.png`: cover image used by the UI

Generated folders such as `build/`, `dist/`, `env/`, and `__pycache__/` should not be committed.

## Run Locally

```powershell
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python OneStepUpdate.py
```

## Build EXE

```powershell
build_exe.bat
```

The build script creates a fresh virtual environment, installs dependencies, and packages the app with PyInstaller.

## Login Behavior

This version does not embed GitHub OAuth client secrets in the source code.
It opens the normal GitHub CLI web login flow:

```powershell
gh auth login --web --hostname github.com -p https
```

Theme preference is stored in the current user's home directory at:

```text
%USERPROFILE%\.onestepupdate_gh_config.json
```

No project-local token file should be committed.

## Notes

- The UI field `目标分支` is passed to `gh release create --target`
- The selected local files are uploaded as Release assets
- This script is focused on Release creation, not on committing and pushing source code changes
