#!/usr/bin/env python3
"""Detect 3p vendors from the SHAPE of response bodies in raw/network/sample_*.network-response.

Some vendors don't appear in network logs because the SaaS proxies them server-side
(creator-data APIs, enrichment vendors, and similar: the SaaS hits them from the
backend, never the browser).
But their data shapes leak through to the responses the browser DOES see.

Reads:
  <study>/raw/network/sample_*.network-response   (response bodies from chrome-devtools get_network_request)

Writes:
  <study>/derived/data-shape-fingerprints.json

Usage:
  fingerprint_data_shapes.py <study-folder>
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Callable


# Signal types:
#   ("key_anywhere", "<key-name>", weight)   : key exists anywhere in the doc (recursive scan)
#   ("path_predicate", "<dotted.path>", predicate_callable, weight)  : predicate on a specific path
#   ("raw_match", "<substring>", weight)     : substring in the raw text
#   ("shape_anywhere", predicate_callable, weight)  : any dict in the tree satisfies a structural predicate

SHAPE_RULES: list[dict] = [
    {
        "vendor": "Phyllo",
        "category": "creator_influencer_data",
        "description": "Creator/influencer data API. Tell-tale: age × gender demographics pivot + countries integer counts + stats.uniqueId + recentPosts list.",
        "signals": [
            # The "demographics" dict has both male and female age-bucket pivots
            ("shape_anywhere", lambda d: isinstance(d, dict) and "male" in d and "female" in d and any(k.startswith(("13-", "18-", "25-", "35-", "45-", "55-", "65-")) for k in d.get("male", {}) if isinstance(d.get("male"), dict)), 0.35),
            # "countries" dict with integer-count values (Phyllo signature; Modash uses lists)
            ("shape_anywhere", lambda d: isinstance(d, dict) and "countries" in d and isinstance(d["countries"], dict) and any(isinstance(v, int) for v in list(d["countries"].values())[:5]), 0.20),
            ("key_anywhere", "platformId", 0.15),
            ("key_anywhere", "isMatchPoolLow", 0.15),
            ("key_anywhere", "uniqueId", 0.10),
            ("key_anywhere", "isNoAuth", 0.05),
        ],
    },
    {
        "vendor": "Modash",
        "category": "creator_influencer_data",
        "description": "Creator data alternative to Phyllo. Different shape, uses 'audience' object with list-based genders/ages/geoCountries.",
        "signals": [
            ("shape_anywhere", lambda d: isinstance(d, dict) and "audience" in d and isinstance(d.get("audience"), dict) and "genders" in d["audience"], 0.40),
            ("key_anywhere", "looksLike", 0.20),
            ("key_anywhere", "audienceLanguages", 0.20),
            ("key_anywhere", "lastPosts", 0.20),
        ],
    },
    {
        "vendor": "Stripe (Customer/Subscription)",
        "category": "payments",
        "description": "Stripe object (customer, subscription, invoice, payment_intent) proxied through SaaS backend.",
        "signals": [
            ("shape_anywhere", lambda d: isinstance(d, dict) and d.get("object") in ["customer", "subscription", "invoice", "payment_intent", "setup_intent"], 0.50),
            ("shape_anywhere", lambda d: isinstance(d, dict) and isinstance(d.get("id"), str) and d["id"].startswith(("cus_", "sub_", "in_", "pi_", "seti_")), 0.50),
        ],
    },
    {
        "vendor": "Stripe Connect (Account)",
        "category": "payments",
        "description": "Stripe Connect account object, present if the SaaS does commission splits / payouts.",
        "signals": [
            ("shape_anywhere", lambda d: isinstance(d, dict) and d.get("object") == "account" and isinstance(d.get("id"), str) and d["id"].startswith("acct_"), 0.70),
            ("key_anywhere", "capabilities", 0.15),
            ("key_anywhere", "requirements", 0.15),
        ],
    },
    {
        "vendor": "WorkOS (Enterprise SSO)",
        "category": "auth",
        "description": "WorkOS organization-binding fields surfaced on agency/tenant rows. Indicates Enterprise SSO capability.",
        "signals": [
            ("key_anywhere", "workosOrganizationId", 0.40),
            ("key_anywhere", "workosEmailDomain", 0.30),
            ("key_anywhere", "workosSsoStatus", 0.30),
        ],
    },
    {
        "vendor": "Evervault (PII tokenization)",
        "category": "pii_pci_tokenization",
        "description": "Evervault team + app keys referenced in response. Suggests sensitive-data encryption (banking, SSN, etc.) is delegated to Evervault.",
        "signals": [
            ("raw_match", "evervault.com", 0.50),
            ("raw_match", "team_", 0.25),
            ("raw_match", "/keys.evervault.com/", 0.25),
        ],
    },
    {
        "vendor": "Stripe (card fields)",
        "category": "payments",
        "description": "Stripe-derived card info embedded in billing response (cardLastFour + expirationMonth/Year).",
        "signals": [
            ("key_anywhere", "cardLastFour", 0.40),
            ("key_anywhere", "expirationMonth", 0.20),
            ("key_anywhere", "expirationYear", 0.20),
            ("key_anywhere", "stripeCustomerId", 0.20),
        ],
    },
    {
        "vendor": "tRPC + SuperJSON",
        "category": "api_style",
        "description": "tRPC + SuperJSON envelope: { result: { data: { json: <payload>, meta: { values: ... } } } }",
        "signals": [
            ("shape_anywhere", lambda d: isinstance(d, dict) and "result" in d and isinstance(d.get("result"), dict) and "data" in d["result"], 0.50),
            ("shape_anywhere", lambda d: isinstance(d, dict) and "json" in d and "meta" in d and isinstance(d.get("meta"), dict) and "values" in d.get("meta", {}), 0.50),
        ],
    },
    {
        "vendor": "AWS CloudFront (signed URL)",
        "category": "media_cdn",
        "description": "CloudFront signed URLs (Key-Pair-Id + Signature + Policy) embedded in response data, pointing to S3-backed media via CloudFront.",
        "signals": [
            ("raw_match", "Key-Pair-Id=", 0.40),
            ("raw_match", "Signature=", 0.30),
            ("raw_match", "cloudfront.net", 0.30),
        ],
    },
    {
        "vendor": "AWS S3 (presigned URL)",
        "category": "media_cdn",
        "description": "S3 presigned URLs (X-Amz-Signature): direct upload/download from S3.",
        "signals": [
            ("raw_match", "X-Amz-Signature=", 0.50),
            ("raw_match", "amazonaws.com/", 0.30),
            ("raw_match", "X-Amz-Date=", 0.20),
        ],
    },
    {
        "vendor": "Cloudflare R2 (presigned URL)",
        "category": "media_cdn",
        "description": "R2 presigned URLs: S3-compatible API on Cloudflare.",
        "signals": [
            ("raw_match", ".r2.cloudflarestorage.com", 0.60),
            ("raw_match", "X-Amz-Signature=", 0.20),
            ("raw_match", "r2.dev", 0.20),
        ],
    },
    {
        "vendor": "Apify TikTok scraper (clockworks/tiktok-scraper)",
        "category": "social_scraping",
        "description": "Apify Actor 'clockworks/tiktok-scraper' output. Distinctive TikTok-internal fields (authorSecUid, challenges array, unique_id) + numeric 19-digit video IDs + p16-sign.tiktokcdn.com avatar URLs. Indicates server-side Apify scrape proxied through SaaS backend.",
        "signals": [
            ("key_anywhere", "authorSecUid", 0.30),
            ("key_anywhere", "challenges", 0.20),
            ("key_anywhere", "tiktokUrl", 0.20),
            ("raw_match", "p16-common-sign.tiktokcdn.com", 0.20),
            ("raw_match", "p16-sign.tiktokcdn", 0.10),
            ("key_anywhere", "engagementRate", 0.10),
            ("key_anywhere", "authorVerified", 0.10),
        ],
    },
    {
        "vendor": "Apify Instagram scraper (apify/instagram-scraper)",
        "category": "social_scraping",
        "description": "Apify Actor 'apify/instagram-scraper' output preserved in a raw_data field. Distinctive: shortCode + childPosts[].dimensionsWidth/Height + displayUrl + latestComments[].",
        "signals": [
            ("shape_anywhere", lambda d: isinstance(d, dict) and "shortCode" in d and "childPosts" in d and isinstance(d.get("childPosts"), list), 0.50),
            ("key_anywhere", "shortCode", 0.15),
            ("key_anywhere", "displayUrl", 0.10),
            ("key_anywhere", "dimensionsWidth", 0.10),
            ("key_anywhere", "latestComments", 0.10),
            ("raw_match", "scontent-", 0.05),
        ],
    },
    {
        "vendor": "Supabase Auth (user session)",
        "category": "auth",
        "description": "Supabase /auth/v1/user response shape. Distinctive: aud='authenticated' + app_metadata.provider + identities[] array with provider-specific identity_data.",
        "signals": [
            ("shape_anywhere", lambda d: isinstance(d, dict) and d.get("aud") == "authenticated" and "app_metadata" in d, 0.50),
            ("key_anywhere", "identities", 0.15),
            ("key_anywhere", "identity_data", 0.15),
            ("key_anywhere", "email_confirmed_at", 0.10),
            ("key_anywhere", "is_anonymous", 0.10),
        ],
    },
    {
        "vendor": "PostgREST / Supabase REST",
        "category": "database",
        "description": "Browser-direct PostgREST query. Distinctive: caller filters with eq.<value> in URL; responses are top-level arrays; embedded resource shapes (e.g., stripe_subscriptions joined with stripe_prices via select=*,nested(*)).",
        "signals": [
            ("raw_match", "supabase.co/rest/v1/", 0.40),
            ("raw_match", "user_id=eq.", 0.20),
            ("raw_match", "?select=", 0.20),
            ("raw_match", "Content-Range", 0.10),
            ("raw_match", "stripe_subscriptions", 0.10),
        ],
    },
    {
        "vendor": "Multi-provider AI router (leaked fallback chain)",
        "category": "llm_router",
        "description": "Server-side AI router that tries multiple model IDs on failure. Detected by error event in SSE stream that names the per-attempt chain (e.g., 'openai:gpt-5.2 -> 429 ... | openai:gpt-4.1 -> 429 ...'). The chain reveals the exact model rotation order, provider boundaries, and which providers are routed cross-fallback (vs within-provider only).",
        "signals": [
            ("raw_match", "could not be completed by provider", 0.40),
            ("raw_match", "Attempts:", 0.20),
            ("raw_match", "openai:gpt-", 0.20),
            ("raw_match", "anthropic:claude-", 0.20),
            ("raw_match", "google:gemini-", 0.20),
            ("raw_match", "-> 429", 0.10),
            ("raw_match", "-> 404", 0.10),
        ],
    },
    {
        "vendor": "Server-Sent Events streaming (LLM chat)",
        "category": "streaming",
        "description": "SSE event stream with structured `data: {type: ...}` framing, typical of LLM chat or generation endpoints. Distinct from chunked-transfer plain text.",
        "signals": [
            ("raw_match", "data: {\"type\":", 0.40),
            ("raw_match", "data: {\"delta\"", 0.30),
            ("raw_match", "data: [DONE]", 0.30),
        ],
    },
    {
        "vendor": "Vercel hosting (originated trace)",
        "category": "hosting",
        "description": "Vercel-specific x-vercel-id '<origin>::<edge>::<request-id>' trace observable in headers + occasionally embedded in error/proxy responses. Confirms Vercel hosting + reveals origin->edge routing topology.",
        "signals": [
            ("raw_match", "x-vercel-id", 0.30),
            ("raw_match", "x-vercel-cache", 0.30),
            ("raw_match", "x-matched-path", 0.20),
            ("raw_match", "server: Vercel", 0.20),
        ],
    },
]


def walk_dicts(obj):
    """Yield every dict found anywhere in the tree (including the root)."""
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk_dicts(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk_dicts(item)


def key_exists_anywhere(obj, key: str) -> bool:
    for d in walk_dicts(obj):
        if key in d:
            return True
    return False


def shape_anywhere(obj, predicate: Callable[[dict], bool]) -> bool:
    for d in walk_dicts(obj):
        try:
            if predicate(d):
                return True
        except Exception:
            continue
    return False


def evaluate_rule(body, raw_text: str, rule: dict) -> tuple[float, list[str]]:
    """Returns (confidence_score, list_of_matched_signal_descriptions)."""
    score = 0.0
    hits: list[str] = []
    for signal in rule["signals"]:
        if signal[0] == "key_anywhere":
            _, key, weight = signal
            if key_exists_anywhere(body, key):
                score += weight
                hits.append(f"key '{key}' present somewhere in body")
        elif signal[0] == "shape_anywhere":
            _, predicate, weight = signal
            if shape_anywhere(body, predicate):
                score += weight
                hits.append(f"structural shape matched (rule-defined)")
        elif signal[0] == "raw_match":
            _, needle, weight = signal
            if needle.lower() in raw_text.lower():
                score += weight
                hits.append(f"raw text contains '{needle}'")
        elif signal[0] == "path_predicate":
            _, path, predicate, weight = signal
            # simple dotted-path lookup
            cur = body
            ok = True
            for part in path.split("."):
                if isinstance(cur, dict) and part in cur:
                    cur = cur[part]
                else:
                    ok = False
                    break
            if ok:
                try:
                    if predicate(cur):
                        score += weight
                        hits.append(f"path '{path}' matched predicate")
                except Exception:
                    pass
    return min(score, 1.0), hits


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    args = p.parse_args()

    study = Path(args.study)
    raw_net = study / "raw" / "network"
    derived = study / "derived"
    derived.mkdir(parents=True, exist_ok=True)

    sample_files = sorted(raw_net.glob("sample_*.network-response")) if raw_net.exists() else []
    if not sample_files:
        (derived / "data-shape-fingerprints.json").write_text(json.dumps({
            "sample_files_scanned": 0,
            "findings": [],
            "note": "No raw/network/sample_*.network-response files. Capture tRPC/GraphQL/REST response bodies via chrome-devtools get_network_request --responseFilePath during Phase 3 to enable data-shape fingerprinting."
        }, indent=2))
        print(f"✓ data-shape-fingerprints.json: 0 samples to scan", file=sys.stderr)
        return 0

    vendor_findings: dict[str, dict] = {}

    for f in sample_files:
        try:
            raw_text = f.read_text()
        except Exception as e:
            print(f"warn: {f.name}: read failed: {e}", file=sys.stderr)
            continue
        # Try JSON parsing, but don't skip the file if it fails (raw_match rules
        # still apply, e.g. SSE event streams, plain-text errors).
        try:
            body = json.loads(raw_text)
        except Exception:
            body = None  # raw_match rules can still fire

        for rule in SHAPE_RULES:
            score, hits = evaluate_rule(body, raw_text, rule)
            if score < 0.5:
                continue
            entry = vendor_findings.setdefault(rule["vendor"], {
                "vendor": rule["vendor"],
                "category": rule["category"],
                "description": rule["description"],
                "best_score": 0.0,
                "evidence": [],
            })
            if score > entry["best_score"]:
                entry["best_score"] = score
            entry["evidence"].append({
                "file": f.name,
                "score": round(score, 2),
                "signals_matched": hits,
            })

    findings = sorted(vendor_findings.values(), key=lambda x: -x["best_score"])
    for fnd in findings:
        fnd["evidence"] = fnd["evidence"][:5]
        fnd["confidence"] = (
            "high" if fnd["best_score"] >= 0.85
            else "moderate" if fnd["best_score"] >= 0.65
            else "low"
        )
        fnd["best_score"] = round(fnd["best_score"], 2)

    out = {
        "sample_files_scanned": len(sample_files),
        "findings": findings,
        "total_vendors_detected": len(findings),
    }
    (derived / "data-shape-fingerprints.json").write_text(json.dumps(out, indent=2))
    print(f"✓ data-shape-fingerprints.json: scanned {len(sample_files)} samples, "
          f"detected {len(findings)} vendor shape(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
