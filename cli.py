#!/usr/bin/env python3
"""
CLI wrapper for RogueGPT core operations.
Usage:
  roguegpt ingest --origin Machine --model openai_gpt-4o_2024-08-06 --content "..." --is-fake --lang en --prompt "..."
  roguegpt ingest --origin Human --outlet "NYT" --url "https://..." --content "..." --lang en
  roguegpt retrieve [--n 5] [--origin Machine] [--model ...] [--lang en] [--is-fake]
  roguegpt stats
  roguegpt models
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import core


def cmd_ingest(args):
    fragment = {
        "Content": args.content,
        "Origin": args.origin,
        "IsFake": args.is_fake,
        "ISOLanguage": args.lang,
        "MachineModel": args.model or "",
        "MachinePrompt": args.prompt or "",
        "HumanOutlet": args.outlet or "",
        "HumanURL": args.url or "",
        "IngestedVia": "cli",
    }
    try:
        result = core.save_fragment(fragment, strict_model=not args.lenient)
        print(json.dumps(result, indent=2, default=str))
    except core.ValidationError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


def cmd_retrieve(args):
    fragments = core.get_random_fragments(
        n=args.n,
        origin=args.origin,
        model=args.model,
        language=args.lang,
        is_fake=args.is_fake,
    )
    for f in fragments:
        for k, v in f.items():
            if hasattr(v, "isoformat"):
                f[k] = v.isoformat()
    print(json.dumps(fragments, indent=2))


def cmd_stats(args):
    total = core.count_fragments()
    human = core.count_fragments(origin="Human")
    machine = core.count_fragments(origin="Machine")
    print(json.dumps({"total": total, "human": human, "machine": machine}, indent=2))


def cmd_models(args):
    models = core.get_valid_models()
    for m in models:
        print(m)


def main():
    parser = argparse.ArgumentParser(prog="roguegpt", description="RogueGPT CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # ingest
    p_ingest = sub.add_parser("ingest", help="Ingest a fragment")
    p_ingest.add_argument("--content", required=True)
    p_ingest.add_argument("--origin", required=True, choices=["Human", "Machine"])
    p_ingest.add_argument("--is-fake", action="store_true", default=False)
    p_ingest.add_argument("--lang", default="en")
    p_ingest.add_argument("--model", default="")
    p_ingest.add_argument("--prompt", default="")
    p_ingest.add_argument("--outlet", default="")
    p_ingest.add_argument("--url", default="")
    p_ingest.add_argument("--lenient", action="store_true", default=False)
    p_ingest.set_defaults(func=cmd_ingest)

    # retrieve
    p_retrieve = sub.add_parser("retrieve", help="Retrieve random fragments")
    p_retrieve.add_argument("--n", type=int, default=1)
    p_retrieve.add_argument("--origin", default=None)
    p_retrieve.add_argument("--model", default=None)
    p_retrieve.add_argument("--lang", default=None)
    p_retrieve.add_argument("--is-fake", type=bool, default=None)
    p_retrieve.set_defaults(func=cmd_retrieve)

    # stats
    p_stats = sub.add_parser("stats", help="Show dataset stats")
    p_stats.set_defaults(func=cmd_stats)

    # models
    p_models = sub.add_parser("models", help="List valid model identifiers")
    p_models.set_defaults(func=cmd_models)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
