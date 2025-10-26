#!/usr/bin/env python3
"""
Quick CLI to exercise Learn endpoints on a running dev backend.

Usage examples:
  python scripts/local/learn_cli.py summary el 251013 1000015419-word-matching-jpg
  python scripts/local/learn_cli.py generate el 251013 1000015419-word-matching-jpg --lemmas βιβλίο,μουσική --num 3 --level A1

Environment:
  API_URL (default http://localhost:3000)
  AUTH_BEARER (optional Supabase JWT for authenticated generation)
"""
import argparse
import json
import os
import sys
from urllib.parse import quote

import urllib.request


def _api_url() -> str:
    return os.environ.get("API_URL", "http://localhost:3000")


def _request(url: str, method: str = "GET", body: dict | None = None):
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("AUTH_BEARER")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        raw = resp.read()
        try:
            return resp.status, json.loads(raw.decode("utf-8"))
        except Exception:
            return resp.status, raw


def do_summary(lang: str, sourcedir: str, sourcefile: str, top: int):
    url = (
        f"{_api_url()}/api/lang/learn/sourcefile/{quote(lang)}/{quote(sourcedir)}/{quote(sourcefile)}/summary?top={top}"
    )
    code, js = _request(url, "GET")
    print(json.dumps({"status": code, "data": js}, ensure_ascii=False, indent=2))


def do_generate(lang: str, sourcedir: str, sourcefile: str, lemmas: list[str], num: int, level: str | None):
    url = (
        f"{_api_url()}/api/lang/learn/sourcefile/{quote(lang)}/{quote(sourcedir)}/{quote(sourcefile)}/generate"
    )
    body = {"lemmas": lemmas, "num_sentences": num, "language_level": level}
    code, js = _request(url, "POST", body)
    print(json.dumps({"status": code, "data": js}, ensure_ascii=False, indent=2))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Learn API CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("summary", help="Fetch priority lemma summary")
    p1.add_argument("lang")
    p1.add_argument("sourcedir")
    p1.add_argument("sourcefile")
    p1.add_argument("--top", type=int, default=20)

    p2 = sub.add_parser("generate", help="Generate sentences + audio")
    p2.add_argument("lang")
    p2.add_argument("sourcedir")
    p2.add_argument("sourcefile")
    p2.add_argument("--lemmas", default="", help="Comma-separated lemma list")
    p2.add_argument("--num", type=int, default=10)
    p2.add_argument("--level", default=None)

    args = parser.parse_args(argv)

    if args.cmd == "summary":
        do_summary(args.lang, args.sourcedir, args.sourcefile, args.top)
        return 0
    if args.cmd == "generate":
        lemmas = [x.strip() for x in (args.lemmas or "").split(",") if x.strip()]
        do_generate(args.lang, args.sourcedir, args.sourcefile, lemmas, args.num, args.level)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


