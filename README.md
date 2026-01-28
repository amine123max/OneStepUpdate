# OneStepUpdate
![OneStepUpdate](OneStepUpdate.png)

A desktop application for pushing local code to GitHub and creating releases with one click.

![OneStepUpdate](OneStepUpdate.ico)

## Features

✨ **One-Click Upload** - Simplify Git workflow, complete code commit, push, tag creation, and release publishing in one go  
🔐 **GitHub OAuth Login** - Secure GitHub account authorization  
🎨 **Theme Switching** - Support for light/dark themes with modern UI  
📦 **Repository Management** - Automatically load your GitHub repository list  
🏷️ **Release Creation** - Automatically create tagged GitHub releases  
💻 **Standalone Application** - No installation or Python environment required

## System Requirements

- Windows 10/11
- Internet connection for GitHub access

## Installation

1. Go to the [Releases](../../releases) page of this repository.
2. Download the latest `OneStepUpdate.exe`.
3. Place it in any folder you prefer (e.g., Desktop).
4. Double-click to run - no installation needed!

> **Note**: Windows Defender might warn you about an "Unrecognized app" because this software is not signed with a paid certificate. Click "More info" -> "Run anyway" to continue.

## Usage Guide

### 1. Login to GitHub

On first launch, click the "Login with GitHub" button. Your browser will open the GitHub authorization page. After authorization, you'll be automatically redirected back to the application.

### 2. Configure Parameters

- **GitHub Repository**: Select target repository from dropdown menu
- **Local Repository Path**: Browse and select your local Git repository folder
- **Files to Add**: Specify files to commit (space-separated, use `.` for all files)
- **Commit Message**: Enter your Git commit message
- **Tag Name**: Enter version tag (e.g., `v1.0.0`)
- **Release Title**: Enter release title
- **Release Description**: Enter release notes (optional)

### 3. Start Upload

Click the "Start Upload" button. The application will automatically:

1. ✅ Add files to Git staging area
2. ✅ Commit changes
3. ✅ Push to GitHub
4. ✅ Create version tag
5. ✅ Push tag to remote
6. ✅ Create GitHub release

Progress will be displayed in the log window at the bottom.

### 4. Theme Toggle

Click the ☀️/🌙 button in the top-left corner to switch between light and dark themes:
- **Light Theme**: Black buttons with white text
- **Dark Theme**: White buttons with black text

Your theme preference is automatically saved.

## Configuration

The application creates an `app_config.json` file in the same directory to store:
- GitHub access token (for automatic login)
- Theme preferences

> [!WARNING]
> **Security Notice**: Keep `app_config.json` private! It contains your GitHub access token. Do not share it or upload it to public repositories.

## FAQ

### Q: Do I need to install Python?
**A:** No! OneStepUpdate.exe is a standalone application that includes everything it needs.

### Q: Token verification failed after login?
**A:** Check your internet connection and ensure you can access GitHub. Try logging in again.

### Q: Push failed?
**A:** Please verify:
- The local path is a valid Git repository (contains a `.git` folder)
- Git is installed on your system
- You have write permissions to the selected GitHub repository

### Q: How do I update to a new version?
**A:** Simply download the new `OneStepUpdate.exe` and replace the old one.

### Q: How do I uninstall?
**A:** Delete `OneStepUpdate.exe` and `app_config.json`. That's it!

### Q: Can I use this on Mac or Linux?
**A:** Currently, OneStepUpdate is only available for Windows.

## Tips

> [!TIP]
> - Use `.` in the "Files to Add" field to add all changed files
> - File names with spaces can be wrapped in quotes: `"my file.txt"`
> - The application remembers your login and theme settings
> - You can browse for files and folders using the browse buttons

## Security & Privacy

- Your GitHub credentials are handled securely through OAuth
- Access tokens are stored locally in `app_config.json`
- No data is sent to third parties
- All communication is directly with GitHub's official API

## Support

If you encounter any issues:
1. Check the log window for error messages
2. Ensure Git is installed on your system
3. Verify your GitHub repository permissions
4. Try logging out and logging in again

