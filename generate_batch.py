#!/usr/bin/env python3
"""
Generate RogueGPT fragments using multiple LLM providers.
Uses: Gemini API (Google), GitHub Copilot proxy (OpenAI, Anthropic).
"""

import json
import os
import sys
import random
import itertools
import time

sys.path.insert(0, os.path.dirname(__file__))
import core

# ─── Config ───────────────────────────────────────────────────────────

MODELS = {
    "google_gemini-3-flash": {
        "provider": "gemini",
        "model": "gemini-3-flash-preview",
    },
    "google_gemini-3-pro-preview": {
        "provider": "gemini",
        "model": "gemini-3-pro-preview",
    },
    "openai_gpt-4.1": {
        "provider": "github",
        "model": "gpt-4.1",
    },
}

SEED_PHRASES = [
    "NASA discovers water on the surface of Mars",
    "European Union bans all social media for minors under 16",
    "Apple announces acquisition of OpenAI for 500 billion dollars",
    "Germany introduces universal basic income of 1500 euros per month",
    "Scientists achieve nuclear fusion breakthrough producing net energy",
    "Amazon to replace all delivery drivers with autonomous drones by 2027",
    "WHO declares new pandemic after mysterious respiratory virus emerges in Southeast Asia",
    "Bitcoin surpasses 500000 dollars as US Federal Reserve announces crypto backing",
    "Major earthquake hits Tokyo causing widespread destruction",
    "France bans all AI-generated content in news media",
]

STYLES_BY_LANG = {
    "en": ["NYT", "CNN", "BBC", "Fox News", "WSJ"],
    "de": ["Spiegel", "BILD", "FAZ", "SZ", "Handelsblatt"],
}

FORMATS = ["tweet", "headline", "short article"]

PROMPT_TEMPLATE = (
    "Write a {format} about '''{seed}''' in {lang_name} in the style of {style}. "
    "Write only the content, no introduction, no explanation, no disclaimer, no translation."
)


def generate_gemini(model: str, prompt: str) -> str:
    """Generate via Google Gemini API."""
    import urllib.request
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 1024}
    }).encode()
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def generate_github(model: str, prompt: str) -> str:
    """Generate via GitHub Models (Azure-backed)."""
    import subprocess
    import urllib.request
    token = subprocess.check_output(["gh", "auth", "token"]).decode().strip()
    url = "https://models.inference.ai.azure.com/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "max_tokens": 1024,
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    })
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()


def generate_openai(model: str, prompt: str) -> str:
    """Generate via OpenAI-compatible API."""
    from openai import OpenAI
    token = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=token)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=1024,
    )
    return resp.choices[0].message.content.strip()


def generate_anthropic(model: str, prompt: str) -> str:
    """Generate via Anthropic API."""
    import urllib.request
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    url = "https://api.anthropic.com/v1/messages"
    payload = json.dumps({
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    })
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read())
    return data["content"][0]["text"].strip()


def generate(roguegpt_model: str, prompt: str) -> str:
    """Route to the correct provider."""
    cfg = MODELS[roguegpt_model]
    provider = cfg["provider"]
    model = cfg["model"]
    
    if provider == "gemini":
        return generate_gemini(model, prompt)
    elif provider == "github":
        return generate_github(model, prompt)
    elif provider == "openai":
        return generate_openai(model, prompt)
    elif provider == "anthropic":
        return generate_anthropic(model, prompt)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=list(MODELS.keys()))
    parser.add_argument("--n-seeds", type=int, default=5, help="Number of seed phrases to use")
    parser.add_argument("--langs", nargs="+", default=["en"])
    parser.add_argument("--formats", nargs="+", default=["short article"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    lang_names = {"en": "English", "de": "German", "fr": "French", "es": "Spanish"}
    seeds = random.sample(SEED_PHRASES, min(args.n_seeds, len(SEED_PHRASES)))

    combos = list(itertools.product(args.models, seeds, args.langs, args.formats))
    print(f"Generating {len(combos)} fragments...")

    success = 0
    errors = 0

    for model_id, seed, lang, fmt in combos:
        styles = STYLES_BY_LANG.get(lang, STYLES_BY_LANG["en"])
        style = random.choice(styles)
        
        prompt = PROMPT_TEMPLATE.format(
            format=fmt, seed=seed, lang_name=lang_names.get(lang, lang), style=style
        )

        print(f"\n[{model_id}] {fmt} | {lang} | {style}")
        print(f"  Seed: {seed[:60]}...")

        if args.dry_run:
            print(f"  (dry run) Prompt: {prompt[:80]}...")
            continue

        try:
            content = generate(model_id, prompt)
            print(f"  Generated: {content[:100]}...")

            result = core.save_fragment({
                "Content": content,
                "Origin": "Machine",
                "MachineModel": model_id,
                "MachinePrompt": prompt,
                "ISOLanguage": lang,
                "IsFake": True,
                "IngestedVia": "cli",
            })
            print(f"  Saved: {result['fragment_id']}")
            success += 1

            # Rate limit: pause between requests (Gemini free tier = 10 RPM)
            time.sleep(4)

        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1
            if "429" in str(e):
                print("  Rate limited, waiting 60s...")
                time.sleep(60)

    print(f"\nDone. Success: {success}, Errors: {errors}")


if __name__ == "__main__":
    main()
