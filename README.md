# SiteSmith

An offline-first website and print-design generator for small businesses. From a phone, a user answers a short guided questionnaire, previews 160 layout and theme combinations using their own content, and exports a complete static website plus print-ready business cards with a scannable QR code.

[View the live app](https://alphapoptart.github.io/sitesmith/)

## Why this project stands out

- Runs the production Python generator directly in the browser with Pyodide
- Works offline after the first visit through service-worker precaching
- Produces byte-identical output across phone and desktop builds
- Generates both a deployable static site and 3.75 × 2.25-inch print assets
- Publishes to GitHub Pages or exports a portable ZIP
- Keeps customer data on-device

## Technical approach

The generator is written in Python. Instead of maintaining a second JavaScript implementation that could drift, SiteSmith ships Pyodide and runs the same generator used by the desktop workflow. Output parity is verified by diffing a phone-generated site against a desktop build across all 20 generated files.

The service worker precaches the application shell, generator, and approximately 13 MB Python runtime. Once cached, the complete create-preview-export workflow runs without a network connection. Publishing is the only feature that requires connectivity.

## Project structure

```text
index.html app.css app.js      Browser application
sw.js manifest.webmanifest     Offline support and installation
py/                            Synced Python generator
py/bridge.py                   Browser-to-Python integration
vendor/pyodide/                Vendored offline Python runtime
sync.py                        Generator sync and cache versioning
```

## Run locally

```bash
python3 -m http.server 8124 --directory .
```

Open <http://localhost:8124>. Service workers require `localhost` or HTTPS, so opening `index.html` directly will not exercise offline mode.

## Update the generator

```bash
python3 sync.py
```

`sync.py` copies the generator into the browser application and stamps a content digest into `sw.js`, ensuring installed clients receive updated assets instead of stale cached files.

## Privacy and security

Form data stays in `localStorage` on the user's device. The application makes no outbound request except to `api.github.com` when the user explicitly chooses Publish. A GitHub token, if saved, remains on that device and is sent only to GitHub.

## Skills demonstrated

Python · JavaScript · Pyodide/WebAssembly · progressive web apps · service workers · offline-first architecture · static-site generation · GitHub API integration · deterministic testing · responsive product design
