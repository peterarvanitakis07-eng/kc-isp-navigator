# URL Management & Sustainability

## Why URLs Break

ISPs reorganize their websites frequently. Specific program pages get moved, renamed, or consolidated. When this happens:
- The hyperlink in your print output returns a 404
- Clients can't access the program information
- It damages trust in your tool

## Solution: Monthly Verification + Smart Fallbacks

### 1. Monthly Link Testing (Part of Pricing Audit)
**Timing:** 1st of each month at 9 AM (automated reminder)  
**Time required:** ~2 minutes  
**Action:** Click each critical URL in the print output and verify it works

**Critical URLs to test every month:**
```
Spectrum: https://www.spectrum.com/resources/internet-wifi/about-spectrum-internet-assist
Verizon: https://www.verizon.com/discounts/verizon-forward/
T-Mobile: https://t-mobile.com/home-internet
All others in ISP_DATA (spot-check the main ones)
```

### 2. Fallback Strategy (If URL Breaks)
If a provider's specific program page breaks, follow this order:

| Scenario | Action |
|----------|--------|
| Program page 404 | Search provider's main site for the program name, find new URL, update ISP_DATA |
| Program page still missing after search | Link to provider's homepage + add note in print output |
| Program discontinued | Remove the low-income program entry, update phone to customer service line |

**Example fallback in code:**
```javascript
// If spectrum.com/assist breaks:
url: "spectrum.com"  // Falls back to homepage
// Customer calls phone number to find program
phone: "1-833-267-6094"
```

### 3. Everfastfiber Pricing (Add It Quarterly)
The PROVIDER_PLANS data for smaller fiber providers may not exist yet. When you run the monthly audit:

**For each empty PROVIDER_PLANS entry:**
1. Visit the provider's website
2. Find their pricing page
3. Look for plans available in KC metro (64127, 64108, Johnson County, etc.)
4. Add 3-4 main tiers to PROVIDER_PLANS object

Example for Everfast:
```javascript
"Everfast Fiber": [
  { name: "Fiber 50", speed: 50, price: 50 },
  { name: "Fiber 100", speed: 100, price: 75 },
  { name: "Fiber 500", speed: 500, price: 125 }
]
```

### 4. Preventing Future URL Breaks

**Short-term (what we do now):**
- Test URLs monthly during pricing audit
- Update quickly if broken
- Add review notes documenting changes

**Medium-term (3–6 months):**
- Track which provider URLs change most frequently
- Consider creating a redirect service (Linktree-style) that you control
- Maintain a URL history log

**Long-term (6+ months):**
- If a provider's URLs are constantly broken, link to their homepage + phone number instead
- Consider QR codes that you generate—more stable than typed URLs

## Commit & Deploy

After updating ISP_DATA with new URLs:
```bash
cd /Users/peterarvanitakis/Downloads/kc-isp-navigator
git add index.html PRICING_AUDIT_CHECKLIST.md
git commit -m "Update ISP URLs from monthly audit - May 2026"
git push origin main
# Railway auto-deploys from main
```

## When URLs Keep Breaking (Architecture Fix)

If a single provider's URL keeps breaking, you have options:

### Option A: Pin to Homepage
```javascript
{name:"Spectrum", url:"spectrum.com", phone:"1-833-267-6094", ...}
// Client can call the number if website is hard to navigate
```

### Option B: Short URL Redirect
Create a custom short URL (e.g., `mysite.com/spectrum-assist`) that redirects to the current correct page. Update the code to use the short URL, and only update the redirect target when the provider's page moves.

### Option C: QR Code
Generate a QR code that links to a landing page you control (e.g., a GitHub wiki or Notion page). Update only the landing page if provider links change—QR code stays the same.

---

## Key Takeaway

**URLs will break. That's not a failure—it's expected.** The sustainable approach is:
1. ✅ Test monthly (catches breaks early)
2. ✅ Fix quickly (1–2 minute update)
3. ✅ Document changes (helps future iterations)
4. ✅ Have a fallback (phone number + homepage if specific link dies)

This is maintainable indefinitely because you're not trying to prevent breaks—you're just catching and fixing them before clients see them.
