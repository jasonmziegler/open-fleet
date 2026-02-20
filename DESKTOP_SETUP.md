# Desktop Setup Guide - Fresh Machine

Complete step-by-step guide to set up your desktop for open-fleet development.

---

## Prerequisites Checklist

Before you start, make sure you have:
- [ ] Windows desktop with admin access
- [ ] Internet connection
- [ ] GitHub account credentials (username: jasonmziegler)

---

## Step 1: Install Git

### Option A: Git for Windows (Recommended)

1. **Download Git:**
   - Go to: https://git-scm.com/download/win
   - Download the latest 64-bit installer

2. **Install Git:**
   - Run the installer
   - **Important settings during install:**
     - Editor: Choose "Use Visual Studio Code" or "Use Vim" (default is fine)
     - PATH: Choose "Git from the command line and also from 3rd-party software"
     - Line endings: "Checkout Windows-style, commit Unix-style" (default)
     - Terminal: "Use MinTTY" (default)
   - Click through remaining defaults
   - Click "Install"

3. **Verify Installation:**
   - Open **Git Bash** (search for it in Start menu)
   - Run:
     ```bash
     git --version
     ```
   - Should show: `git version 2.x.x`

---

## Step 2: Configure Git

**In Git Bash, run these commands:**

```bash
# Set your name (will appear in commits)
git config --global user.name "Jason Ziegler"

# Set your email (use your GitHub email)
git config --global user.email "jason@insightfulautomation.com"

# Verify configuration
git config --list
```

**Expected output:**
```
user.name=Jason Ziegler
user.email=jason@insightfulautomation.com
...
```

---

## Step 3: Create Development Directory

```bash
# Navigate to C: drive
cd /c/

# Create dev directory
mkdir dev

# Navigate into it
cd dev
```

---

## Step 4: Clone Repository from GitHub

### Option A: HTTPS (Simple, Recommended)

```bash
# Clone the repository
git clone https://github.com/jasonmziegler/open-fleet.git

# Navigate into the project
cd open-fleet

# Verify you have all commits
git log --oneline
```

**Expected output:**
```
1ef57fc Add README.md - Project overview and documentation
3fbf0f0 Add BMAD framework (Business Model Agent Design)
5348c33 Add .gitignore for Python AI agent project
286a309 Complete product brief: Target users, success metrics, and MVP scope
0cc37cd Add product brief: open-fleet MVP vision and strategy
```

### Option B: SSH (More Secure, Requires Setup)

**Skip this if you used Option A**

<details>
<summary>Click to expand SSH setup instructions</summary>

1. **Generate SSH Key:**
   ```bash
   ssh-keygen -t ed25519 -C "jason@insightfulautomation.com"
   ```
   - Press Enter for default location
   - Press Enter twice for no passphrase (or set one if you prefer)

2. **Copy Public Key:**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   - Copy the entire output (starts with `ssh-ed25519`)

3. **Add to GitHub:**
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Title: "Desktop PC"
   - Paste the key
   - Click "Add SSH key"

4. **Clone with SSH:**
   ```bash
   cd /c/dev
   git clone git@github.com:jasonmziegler/open-fleet.git
   cd open-fleet
   ```

</details>

---

## Step 5: Install Python

1. **Download Python:**
   - Go to: https://www.python.org/downloads/
   - Download **Python 3.11** or **Python 3.12** (recommended)

2. **Install Python:**
   - Run installer
   - ⚠️ **IMPORTANT:** Check "Add Python to PATH" at the bottom!
   - Click "Install Now"
   - Wait for installation to complete

3. **Verify Installation:**
   ```bash
   # Close and reopen Git Bash (to refresh PATH)
   python --version
   ```
   - Should show: `Python 3.11.x` or `Python 3.12.x`

   ```bash
   pip --version
   ```
   - Should show: `pip 24.x.x`

---

## Step 6: Set Up Python Virtual Environment

**In Git Bash, from the project directory:**

```bash
# Make sure you're in the project directory
cd /c/dev/open-fleet

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/Scripts/activate
```

**Your prompt should now show `(venv)` at the beginning:**
```
(venv) jason@DESKTOP /c/dev/open-fleet
```

**To deactivate later (don't do this now):**
```bash
deactivate
```

---

## Step 7: Install Development Dependencies

**Create requirements.txt (we'll add to this as we build):**

```bash
# Initial dependencies for MVP
cat > requirements.txt << 'EOF'
# Slack Integration
slack-bolt==1.18.0
slack-sdk==3.27.0

# Gmail API
google-api-python-client==2.122.0
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.0

# LLM Integration (Gemini option)
google-generativeai==0.4.0

# HTTP & Async
requests==2.31.0
aiohttp==3.9.3

# Environment Variables
python-dotenv==1.0.1

# Development Tools
pytest==8.0.2
black==24.2.0
flake8==7.0.0
EOF
```

**Install dependencies:**

```bash
# With venv activated
pip install -r requirements.txt
```

**This will take 2-3 minutes. Wait for it to complete.**

---

## Step 8: Install Code Editor (VS Code Recommended)

1. **Download VS Code:**
   - Go to: https://code.visualstudio.com/
   - Download Windows installer

2. **Install VS Code:**
   - Run installer
   - Accept defaults
   - **Check:** "Add to PATH" (important!)
   - Click "Install"

3. **Open Project in VS Code:**
   ```bash
   # From Git Bash in project directory
   code .
   ```

4. **Install Recommended Extensions:**
   - Python (Microsoft)
   - Pylance (Microsoft)
   - GitLens (optional but useful)

   **Or install via terminal:**
   ```bash
   code --install-extension ms-python.python
   code --install-extension ms-python.vscode-pylance
   code --install-extension eamodio.gitlens
   ```

---

## Step 9: Verify Everything Works

**Run these verification commands:**

```bash
# 1. Check Git is configured
git config --list | grep user

# 2. Check Python version
python --version

# 3. Check pip packages installed
pip list

# 4. Check you're in the right directory
pwd
# Should show: /c/dev/open-fleet

# 5. Check git status
git status
# Should show: "On branch master, Your branch is up to date with 'origin/master'"

# 6. List files
ls -la
# Should show: README.md, .gitignore, _bmad/, _bmad-output/, etc.
```

---

## Step 10: Create Your First Branch for Development

```bash
# Make sure you're on master and up to date
git checkout master
git pull

# Create a new branch for Sprint 1 (Gmail API integration)
git checkout -b feature/gmail-api-integration

# Verify you're on the new branch
git branch
# Should show: * feature/gmail-api-integration (with asterisk)
```

---

## Step 11: Test Python Environment

**Create a test file to verify everything works:**

```bash
# Create test file
cat > test_setup.py << 'EOF'
#!/usr/bin/env python3
"""
Test script to verify desktop setup is complete.
"""

import sys
import slack_bolt
import google.auth
import dotenv

def main():
    print("✅ Python version:", sys.version)
    print("✅ Slack Bolt installed:", slack_bolt.__version__)
    print("✅ Google Auth installed: OK")
    print("✅ Python dotenv installed: OK")
    print("\n🎉 Desktop setup complete! Ready to develop.")

if __name__ == "__main__":
    main()
EOF

# Run test
python test_setup.py
```

**Expected output:**
```
✅ Python version: 3.11.x (or 3.12.x)
✅ Slack Bolt installed: 1.18.0
✅ Google Auth installed: OK
✅ Python dotenv installed: OK

🎉 Desktop setup complete! Ready to develop.
```

---

## Step 12: Set Up Environment Variables (For Later)

**Create `.env` file (don't commit this - already in .gitignore):**

```bash
# This is for later when you get API keys
cat > .env << 'EOF'
# Slack
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_APP_TOKEN=xapp-your-token-here

# Gmail API
GMAIL_CREDENTIALS_FILE=credentials.json

# Gemini API (if using cloud option)
GEMINI_API_KEY=your-api-key-here

# LM Studio (if using local option)
LM_STUDIO_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=qwen2.5-coder

# Environment
ENVIRONMENT=development
EOF
```

**Note:** This file is already in `.gitignore` so it won't be committed.

---

## Troubleshooting

### Git Bash shows "command not found"
- **Solution:** Close and reopen Git Bash after installing Python or Git

### Python not found after installation
- **Solution:** Make sure you checked "Add Python to PATH" during install. Reinstall if needed.

### pip install fails with SSL errors
- **Solution:**
  ```bash
  pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
  ```

### VS Code doesn't open from terminal
- **Solution:** Make sure you checked "Add to PATH" during VS Code install

### "Permission denied" errors
- **Solution:** Run Git Bash as Administrator (right-click → Run as Administrator)

---

## Quick Reference: Daily Development Workflow

**Starting work each day:**

```bash
# 1. Open Git Bash
# 2. Navigate to project
cd /c/dev/open-fleet

# 3. Activate virtual environment
source venv/Scripts/activate

# 4. Pull latest changes from GitHub
git pull

# 5. Check current branch
git branch

# 6. Start coding!
code .
```

**Saving your work:**

```bash
# 1. Check what changed
git status

# 2. Add changes
git add .

# 3. Commit with message
git commit -m "Your commit message here"

# 4. Push to GitHub
git push

# 5. Deactivate venv when done
deactivate
```

---

## Next Steps After Setup

Once your desktop is set up, you're ready for:

1. **Sprint 1: Gmail API Integration (Week 1-2)**
   - Set up Google Cloud Console
   - Configure Gmail API credentials
   - Test reading emails

2. **Sprint 2: LLM Integration (Week 2-3)**
   - Set up LM Studio OR Gemini
   - Test action item extraction
   - Iterate on prompts

3. **Sprint 3: Slack Integration (Week 3-4)**
   - Create Slack app
   - Set up Cloudflare tunnel
   - Test end-to-end flow

---

## Summary

You should now have:
- ✅ Git installed and configured
- ✅ Repository cloned from GitHub
- ✅ Python 3.11+ installed
- ✅ Virtual environment created and activated
- ✅ Dependencies installed
- ✅ VS Code installed with Python extensions
- ✅ Development branch created
- ✅ Environment file template created
- ✅ Ready to start Sprint 1!

---

**Questions? Issues?**

If you run into problems, check:
1. This troubleshooting section
2. Git Bash is running as Administrator
3. All installations completed successfully
4. Virtual environment is activated (shows `(venv)` in prompt)

**Ready to build!** 🚀
