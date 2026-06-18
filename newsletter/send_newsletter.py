#!/usr/bin/env python3
"""
Daily AI Digest — Newsletter Sender
Sends newsletter email to all Cloudflare D1 subscribers when a new post is published.

Usage:
    python3 send_newsletter.py --slug <post-slug> --title <post-title> --url <post-url>

This is called automatically by the daily cron pipeline after a new post is built and pushed.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import os

# ─── Config ───
# Change these after deploying the Worker
WORKER_URL = os.environ.get("NEWSLETTER_WORKER_URL", "https://daily-ai-digest-newsletter.YOUR_SUBDOMAIN.workers.dev")
ADMIN_SECRET = os.environ.get("NEWSLETTER_ADMIN_SECRET", "CHANGE_ME_TO_RANDOM_STRING")


def send_newsletter(slug: str, title: str, url: str) -> dict:
    """Send newsletter to all subscribers via Cloudflare Worker."""
    payload = json.dumps({
        "secret": ADMIN_SECRET,
        "post_slug": slug,
        "post_title": title,
        "post_url": url,
    }).encode()

    req = urllib.request.Request(
        f"{WORKER_URL}/api/send",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"HTTP Error {e.code}: {body}", file=sys.stderr)
        return {"error": str(e.code), "detail": body}
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return {"error": str(e)}


def list_subscribers() -> dict:
    """List all subscribers (admin only)."""
    req = urllib.request.Request(
        f"{WORKER_URL}/api/subscribers?secret={ADMIN_SECRET}",
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Daily AI Digest Newsletter Sender")
    sub = parser.add_subparsers(dest="command")

    # Send command
    send_cmd = sub.add_parser("send", help="Send newsletter for a new post")
    send_cmd.add_argument("--slug", required=True, help="Post slug (e.g., 2026-06-18)")
    send_cmd.add_argument("--title", required=True, help="Post title")
    send_cmd.add_argument("--url", required=True, help="Post URL path (e.g., /posts/2026-06-18.html)")

    # List command
    sub.add_parser("list", help="List all subscribers")

    # Count command
    sub.add_parser("count", help="Count active subscribers")

    args = parser.parse_args()

    if args.command == "send":
        print(f"📧 Sending newsletter: {args.title}")
        print(f"   Slug: {args.slug}")
        print(f"   URL:  {args.url}")
        result = send_newsletter(args.slug, args.title, args.url)
        if "error" in result:
            print(f"❌ Failed: {result}")
            sys.exit(1)
        print(f"✅ Sent to {result.get('sent', 0)} subscribers")
        if result.get("failed", 0) > 0:
            print(f"⚠️  {result['failed']} failed")
    elif args.command in ("list", "count"):
        result = list_subscribers()
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        subs = result.get("subscribers", [])
        active = [s for s in subs if s.get("is_active")]
        if args.command == "count":
            print(f"Active subscribers: {len(active)}")
        else:
            print(f"Total: {len(subs)} | Active: {len(active)}")
            for s in subs:
                status = "✅" if s.get("is_active") else "❌"
                print(f"  {status} {s['email']} — {s['subscribed_at']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
