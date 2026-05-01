# ISP Pricing Audit Checklist (Monthly)

**Time:** ~2-3 minutes  
**When:** 1st of each month (automated reminder at 9 AM)  
**File to update:** `/Users/peterarvanitakis/Downloads/kc-isp-navigator/index.html` (ISP_DATA array, lines 587–618)

---

## SPECTRUM CHECK

📍 Visit: https://www.spectrum.com/services/missouri/kansas-city

**Watch for these fields in ISP_DATA (around line 589):**
- `Internet Advantage`: $30/mo → update `phone:"1-800-288-2020"` if changed
- `Internet Premier`: $50/mo → most popular, promotional pricing
- `Internet Gig`: varies → check for promotional rates
- `Internet Assist`: $17.99–25/mo → low-income program

**Sample line to update:**
```javascript
{name:"Spectrum",tech:"Cable/Fiber",speed:1000,category:"fiber-cable",url:"spectrum.com/assist",counties:[...],phone:"1-833-267-6094",lowIncome:{prog:"Spectrum Internet Assist",price:"$17.99/mo",spd:"30 Mbps",...}}
```

---

## T-MOBILE CHECK

📍 Visit: https://www.t-mobile.com/home-internet/plans

**Watch for these fields in ISP_DATA (around line 608):**
- Standard pricing: $50/mo (or $60 without AutoPay)
- AutoPay discount: $40–$70/mo
- Voice line bundle discount: -$15/mo
- New customer rebate: $200 (if still running)

**Sample line to update:**
```javascript
{name:"T-Mobile",tech:"5G Home Internet",speed:245,category:"wireless",url:"t-mobile.com/home-internet",counties:[...],phone:"1-844-275-9310",lowIncome:{prog:"Project 10Million",price:"Free",spd:"100GB/yr hotspot",...}}
```

---

## BROADBANDNOW CHECK (Reference Only)

📍 Visit: https://broadbandnow.com/Missouri/Kansas-City

**Purpose:** Sanity check—make sure what Spectrum/T-Mobile claim matches what comparison sites show.  
**Action:** If prices look significantly different, investigate before updating.

---

## HOW TO UPDATE ISP_DATA

1. **Open** `/Users/peterarvanitakis/Downloads/kc-isp-navigator/index.html`
2. **Find** the ISP_DATA array (starts line 587)
3. **Locate** the ISP entry (Spectrum, T-Mobile, etc.)
4. **Update** the fields:
   - `price`: Promo rate (e.g., `"$30/mo"`)
   - `lowIncome.price`: If applicable (e.g., `"$17.99/mo"`)
   - `phone`: Keep as-is (already accurate)
5. **If promotional pricing changed**, add/update `updated:"Apr 2026"` field for clarity
6. **Save** the file
7. **Test** locally to make sure prices display correctly

---

## RED FLAGS (Stop & Investigate)

- ❌ Price jumped >$20/mo unexpectedly
- ❌ Low-income program no longer available
- ❌ Phone number is different (verify it's correct)
- ❌ Speed tier changed (e.g., Spectrum Premier now 300 Mbps instead of 500)
- ❌ **URL is broken** (404 error or page not found) — update to correct landing page

If you spot any red flags, double-check on the official website and note the change in a `reviewNote` field.

---

## LINK CHECKING (NEW)

When visiting each provider, also verify the `url` field in ISP_DATA is correct:

- **Spectrum:** Should link to: `www.spectrum.com/resources/internet-wifi/about-spectrum-internet-assist`
- **Verizon:** Should link to: `www.verizon.com/discounts/verizon-forward/`
- **Others:** Check if links still work (don't get 404 errors)

If a URL returns 404, find the correct page and update the `url` field in ISP_DATA.

---

## TEMPLATE FOR REVIEW NOTE

```javascript
reviewNote:"April 2026 update: Spectrum Premier promo increased from $40 to $50/mo. Confirmed on spectrum.com/services/missouri/kansas-city"
```

---

## QUICK REFERENCE: FIELD LOCATIONS

| Provider | Start Line | Key Fields |
|----------|-----------|-----------|
| Spectrum | 590 | price, lowIncome.prog, lowIncome.price, phone |
| T-Mobile | 608 | price, lowIncome, phone |
| All Others | 587-618 | price, phone (if applicable) |

---

**✅ Done?**  
Save the file, quick test in browser, mark as complete.

**⏰ Next audit:**  
May 1st, 9 AM (automatic reminder)
