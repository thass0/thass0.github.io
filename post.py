#!/usr/bin/env python3

import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

MBLOG_FILENAME = "mblog.json"
BLOG_DIR = Path(os.environ["BLOG_DIR"])
MBLOG_FILE = BLOG_DIR / MBLOG_FILENAME

assert BLOG_DIR.exists()
assert MBLOG_FILE.exists()

def git(*args):
    return subprocess.run(["git", "-C", str(BLOG_DIR), *args], check=True, capture_output=True, text=True)

assert git("diff", "--staged", "--quiet").returncode == 0
assert git("symbolic-ref", "--short", "HEAD").stdout.strip() == "main"


posts = json.loads(MBLOG_FILE.read_text(encoding="utf-8"))
next_id = (max(p["id"] for p in posts) + 1) if posts else 1
editor = os.environ.get("EDITOR", "nano")

with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
    tmp = f.name
try:
    subprocess.run([editor, tmp], check=True)
    text = Path(tmp).read_text(encoding="utf-8").strip()
finally:
    os.unlink(tmp)

assert text

post = {"id": next_id, "date": datetime.now().isoformat(), "text": text}
posts.append(post)
MBLOG_FILE.write_text(json.dumps(posts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Added post {next_id}.")

git("add", MBLOG_FILENAME)
git("commit", "-m", f"mblog: Add post {next_id}")
git("push")

