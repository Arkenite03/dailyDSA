# GitHub Repository Setup Checklist

Before pushing to GitHub, ensure:

## ✅ Security Checklist

- [ ] `credentials.json` is NOT committed (already in `.gitignore`)
- [ ] `run_bot.sh` is NOT committed (contains tokens, in `.gitignore`)
- [ ] `setup_env.sh` is NOT committed (contains tokens, in `.gitignore`)
- [ ] `test_config.py` is NOT committed (contains tokens, in `.gitignore`)
- [ ] No hardcoded tokens in any `.py` files
- [ ] No hardcoded tokens in `README.md`
- [ ] Use `.example` files for templates

## 📁 Files Safe to Commit

- ✅ All `.py` files (bot.py, handlers.py, etc.)
- ✅ `requirements.txt`
- ✅ `README.md` (without tokens)
- ✅ `DEPLOYMENT.md`
- ✅ `.gitignore`
- ✅ `*.example` files (templates)
- ✅ `dsa-bot.service` (template)

## 📁 Files to Keep Local Only

- ❌ `credentials.json`
- ❌ `run_bot.sh` (with actual tokens)
- ❌ `setup_env.sh` (with actual tokens)
- ❌ `test_config.py` (with actual tokens)
- ❌ Any `.env` files

## 🚀 Quick Git Setup

```bash
# Initialize git (if not already done)
git init

# Add all safe files
git add *.py *.txt *.md *.example .gitignore dsa-bot.service

# Verify what will be committed
git status

# Commit
git commit -m "Initial commit: DSA Telegram Bot"

# Add remote (replace with your GitHub repo URL)
git remote add origin https://github.com/yourusername/dsaTelegram.git

# Push
git push -u origin main
```

## 🔐 For RedHat Deployment

After cloning on the server:
1. Upload `credentials.json` separately (not via git)
2. Copy `.example` files and add your tokens
3. Follow `DEPLOYMENT.md` for systemd setup
