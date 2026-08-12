#!/usr/bin/env python3
"""Copy the generator out of the sitesmith skill into this app.

The app runs the real generator under Pyodide, so there is no port and nothing to
keep in step by hand — but the files do need copying in whenever the skill changes.
Run this, commit, push. Pages redeploys itself.

    python3 sync.py            # copy, then report what changed
    python3 sync.py --check    # exit 1 if out of date, for a pre-push hook
"""

import filecmp
import hashlib
import json
import os
import re
import shutil
import sys

SKILL = os.path.expanduser("~/.claude/skills/sitesmith/scripts")
HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "py")

# bridge.py belongs to the app, not the skill, so it is never overwritten.
MODULES = ["content.py", "design.py", "css.py", "layouts.py", "cards.py",
           "qr.py", "sitesmith.py"]


def main():
    check = "--check" in sys.argv
    if not os.path.isdir(SKILL):
        sys.exit(f"Skill not found at {SKILL}")

    os.makedirs(DEST, exist_ok=True)
    changed, missing = [], []
    for name in MODULES:
        src = os.path.join(SKILL, name)
        dst = os.path.join(DEST, name)
        if not os.path.exists(src):
            missing.append(name)
            continue
        same = os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False)
        if not same:
            changed.append(name)
            if not check:
                shutil.copy2(src, dst)

    if missing:
        sys.exit(f"Missing from the skill: {', '.join(missing)}")

    if check:
        if changed:
            print("out of date: " + ", ".join(changed))
            print("run: python3 sync.py")
            sys.exit(1)
        print("py/ matches the skill")
        return

    # One digest over everything a browser caches. Stamping it into sw.js means a
    # deploy can never leave a phone running a half-old app: any byte change makes
    # a new cache name, which drops the previous one on activate.
    digest = hashlib.sha256()
    for rel in sorted(_cacheable()):
        digest.update(rel.encode())
        digest.update(open(os.path.join(HERE, rel), "rb").read())
    version = digest.hexdigest()[:12]

    with open(os.path.join(DEST, "version.json"), "w") as fh:
        json.dump({"generator": version}, fh)

    sw_path = os.path.join(HERE, "sw.js")
    if os.path.exists(sw_path):
        sw = open(sw_path, encoding="utf-8").read()
        stamped = re.sub(r'var VERSION = "[^"]*";',
                         f'var VERSION = "sitesmith-{version}";', sw, count=1)
        if stamped != sw:
            open(sw_path, "w", encoding="utf-8").write(stamped)
            print(f"service worker cache -> sitesmith-{version}")

    if changed:
        print("updated: " + ", ".join(changed))
    else:
        print("py/ already matched the skill")
    print("\nnext:\n  git add -A && git commit -m 'sync generator' && git push")


def _cacheable():
    """Every file the service worker precaches, relative to the app root."""
    out = []
    for rel_dir in ("", "py", "icons"):
        d = os.path.join(HERE, rel_dir)
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if name.startswith("."):
                continue
            rel = os.path.join(rel_dir, name) if rel_dir else name
            if os.path.isfile(os.path.join(HERE, rel)) and not name.endswith(".pyc"):
                if name in ("sw.js", "version.json", "sync.py", "README.md"):
                    continue
                out.append(rel)
    return out


if __name__ == "__main__":
    main()
