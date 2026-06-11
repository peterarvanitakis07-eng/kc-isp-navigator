# KC Digital Navigator ISP Tool

A field tool that helps Kansas City Digital Navigators find affordable internet options for the people sitting across from them. Enter a client's address, get the internet providers available at that location, the low-income programs they qualify for, current pricing, and a printable handout the client can take home.

Live tool: [kc-isp-navigator on GitHub Pages](https://peterarvanitakis07-eng.github.io/kc-isp-navigator/)

## The Problem

When the federal Affordable Connectivity Program ended, millions of households lost their internet subsidy and the navigators who help them lost their simplest answer. "What can I actually afford?" became hard to answer again. In Kansas City, Digital Navigators in the Digital Life Exchange (DLX) program sit with clients one on one and have minutes, not hours, to give a clear, trustworthy answer about internet options at a specific address.

The information exists, but it is scattered: FCC availability data in one place, each provider's low-income program buried on its own site, pricing that changes, and program pages that move or break. A navigator should not have to open eight browser tabs while a client waits.

## What It Does

- Looks up internet providers available at a client's address using FCC block-level availability data
- Surfaces low-income and discount programs by provider (for example Spectrum Internet Assist, Verizon Forward, T-Mobile Home Internet)
- Shows current pricing tiers and a customer-service phone number for each provider
- Generates a clean, print-friendly handout the client can take with them
- Works as an installable Progressive Web App: it runs on a phone or tablet, installs to the home screen, and keeps working offline in the field where Wi-Fi is unreliable

## How It Works

- **Frontend (this repo):** a single-page Progressive Web App. Provider data, pricing, and program links live in a structured `ISP_DATA` object so a non-engineer can update them during a monthly audit. A service worker (`sw.js`) and `manifest.json` make it installable and offline-capable.
- **Backend ([kc-isp-proxy](https://github.com/peterarvanitakis07-eng/kc-isp-proxy)):** a lightweight JavaScript geocoding proxy that turns a typed address into the coordinates and census block needed for the FCC lookup.
- **Deployment:** GitHub Pages serves the app; the proxy is deployed on Railway and redeploys automatically from `main`.
- **Maintenance:** a monthly pricing-and-URL audit keeps program links and prices current. The approach assumes provider URLs will break and is built to catch and fix them quickly rather than prevent them. See [`docs/`](./docs).

## What I Learned

I built this as a non-engineer working in digital equity, with Claude as a build partner. Three things stuck:

1. **Build for the moment of use, not the demo.** The hardest design constraint was not the data, it was the two-minute window a navigator has with a client. Every decision (offline support, a printable handout, one address field) came from picturing that table, not a feature list.
2. **Plan for decay.** Provider pages move constantly. Treating broken links as expected, and building a fast monthly fix routine, made the tool maintainable by one person instead of fragile.
3. **Structure the data so a human can own it.** Keeping provider info in a plain, editable object means the people who use the tool can keep it accurate without touching application logic.

## Status

Built and deployed. Actively maintained through a monthly audit. Open issues track pricing refreshes and provider data additions.

## License

MIT
