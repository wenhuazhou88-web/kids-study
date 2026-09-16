#!/usr/bin/env python3
"""用 GitHub Contents API 提交文件到 kids-study 仓库（GitHub 网页/HTTPS git 被墙时的推送通道）。

用法：
  python3 publish-api.py ai-tutor.html [更多文件名...]
  python3 publish-api.py --all        # 提交仓库内所有已跟踪的 *.html

依赖：gh CLI 已登录（token 从 `gh auth token` 读，不落盘）。
"""
import base64
import json
import subprocess
import sys
import urllib.request

REPO = "wenhuazhou88-web/kids-study"
BRANCH = "main"


def token():
    return subprocess.check_output(["gh", "auth", "token"]).decode().strip()


def api(method, path, payload=None, tok=""):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}{path}",
        method=method,
        data=json.dumps(payload).encode() if payload else None,
        headers={
            "Authorization": f"Bearer {tok}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "hermes-publish",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode() or "{}")


def remote_sha(path, tok):
    try:
        return api("GET", f"/contents/{path}?ref={BRANCH}", tok=tok).get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def publish(path, message, tok):
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    payload = {"message": message, "content": content, "branch": BRANCH}
    sha = remote_sha(path, tok)
    if sha:
        payload["sha"] = sha
    res = api("PUT", f"/contents/{path}", payload, tok=tok)
    print(f"OK {path} -> {res['commit']['sha'][:10]}  {res['commit']['html_url']}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    if args == ["--all"]:
        args = subprocess.check_output(
            ["git", "ls-files", "*.html"], cwd="/Users/wh-zz/周周玩hermes"
        ).decode().split()
    tok = token()
    for path in args:
        publish(path, f"update {path} (via API publish)", tok)
    return 0


if __name__ == "__main__":
    sys.exit(main())
