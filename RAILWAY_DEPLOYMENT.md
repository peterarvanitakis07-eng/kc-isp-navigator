# Railway Deployment Quick Reference

## Current Status
- **Repository:** GitHub main branch (all changes are pushed)
- **Deployment:** Railway (auto-deploys from main via webhook)
- **Last commit:** `Add URL verification to monthly pricing audit checklist`

## Quick Test: Verify Deployed Version

1. **Open the deployed site** (replace with your Railway domain):
   ```
   https://kc-isp-navigator-production.up.railway.app
   ```

2. **Test the "Print for Client" output:**
   - Enter test address: `Santa Fe Towers, Overland Park, KS 66204`
   - Click "Print for Client"
   - Check if:
     - ✅ Everfastfiber shows pricing (Fiber 50, 100, 500)
     - ✅ Spectrum link works: https://www.spectrum.com/resources/internet-wifi/about-spectrum-internet-assist
     - ✅ Verizon link works: https://www.verizon.com/discounts/verizon-forward/
     - ✅ Community resource links are hyperlinked (jocolibrary.org, etc.)

## If Changes Aren't Showing

**Most common cause:** Railway hasn't redeployed yet after your code push.

### Option 1: Force Railway Redeploy (Fastest)
1. Go to: https://railway.app/dashboard
2. Find your `kc-isp-navigator` project
3. Click on the **Deployments** tab
4. Click the **three dots** (⋯) next to the latest deployment
5. Select **"Redeploy"**
6. Wait 1-2 minutes for the rebuild to complete
7. Test the site again

### Option 2: Trigger via GitHub Commit
Push a new commit to `main` to trigger Railway's webhook:
```bash
cd /Users/peterarvanitakis/Downloads/kc-isp-navigator
git add index.html
git commit -m "Force redeploy trigger"
git push origin main
# Wait 1-2 minutes, then test the site
```

### Option 3: Check Deployment Logs
If changes still aren't showing after redeploy:
1. Go to https://railway.app/dashboard
2. Click your project → **Deployments** tab
3. Click the latest deployment
4. Scroll to **Build Logs** and **Deploy Logs**
5. Look for errors (usually marked in red)

## What Gets Deployed

- ✅ `index.html` (your main application file)
- ✅ Static assets (CSS, images, etc.)
- ✅ Node.js dependencies (if using a backend)
- ⚠️ Does NOT include: local test files, .gitignore'd files

**If you change something in the repo and it's not showing:**
- Verify the file is committed: `git status` should show nothing
- Verify the file is pushed: `git log origin/main` should show your commit
- Force a Railway redeploy (Option 1 above)

## Checking if Code Matches Deployed Version

Run this from the project directory:
```bash
cd /Users/peterarvanitakis/Downloads/kc-isp-navigator
git log --oneline -5
```

Compare the output with your latest changes. The top commit should be your most recent fix.

---

## Troubleshooting Checklist

| Issue | Check | Fix |
|-------|-------|-----|
| "Still seeing old version" | Is commit in `git log`? | Push the commit: `git push origin main` |
| "Changes not in git log" | Did you run `git add` and `git commit`? | Commit the file: `git add file.txt && git commit -m "..."` |
| "Deployed after push but still old" | Check Railway Deployments tab | Force redeploy (Option 1 above) |
| "Build logs show errors" | Read the error message in Deployments tab | Fix the error in code, push, redeploy |
| "Still broken after all this" | Check browser cache | Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac) |

---

## Safe Deployment Workflow

Always follow this before assuming something is broken:

1. ✅ Make code change in `index.html`
2. ✅ Test locally in your browser
3. ✅ Run: `git add index.html`
4. ✅ Run: `git commit -m "descriptive message"`
5. ✅ Run: `git push origin main`
6. ✅ Wait 1–2 minutes
7. ✅ Visit the Railway URL and hard-refresh (Cmd+Shift+R)
8. ✅ Test the feature you changed
9. ⚠️ If still broken, force redeploy via Railway dashboard

This eliminates 99% of "it's not working" issues—usually it's just a cache or redeploy delay.
