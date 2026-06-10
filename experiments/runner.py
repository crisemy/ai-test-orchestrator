"""
Prompt experiment runner.

Run the pipeline with different model/temperature/prompt variants
and compare KPIs across experiments.

Usage:
    python experiments/runner.py --url "..." --feature "login" --experiment "test-v1"
"""

import subprocess
import os
import json
import argparse
from datetime import datetime, timezone

EXPERIMENTS_DIR = "experiments"
PIPELINE_CMD = ["python", "orchestrator.py"]


def run_experiment(url, feature, model, temperature, prompt_variant, label):
    os.makedirs(EXPERIMENTS_DIR, exist_ok=True)

    experiment_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    card = {
        "experiment_id": experiment_id,
        "label": label,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": {
            "url": url,
            "feature": feature,
            "model": model,
            "temperature": temperature,
            "prompt_variant": prompt_variant,
        },
        "result": None,
    }

    print(f"\n{'='*60}")
    print(f"Experiment: {label}")
    print(f"Model: {model} | Temperature: {temperature}")
    print(f"{'='*60}\n")

    # Run pipeline
    cmd = PIPELINE_CMD + [
        "--url", url,
        "--feature", feature,
        "--model", model,
        "--engine", "ollama",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    card["result"] = {
        "exit_code": result.returncode,
        "stdout": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
        "stderr": result.stderr[-1000:] if result.stderr and len(result.stderr) > 1000 else (result.stderr or ""),
    }

    # Save experiment card
    card_path = os.path.join(EXPERIMENTS_DIR, f"{experiment_id}_{label.replace(' ', '-')}.json")
    with open(card_path, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2)

    print(f"\nExperiment saved: {card_path}")
    return card


def compare_experiments():
    """Load all experiment cards and show comparison."""
    if not os.path.exists(EXPERIMENTS_DIR):
        print("No experiments found.")
        return

    cards = []
    for fname in sorted(os.listdir(EXPERIMENTS_DIR)):
        if fname.endswith(".json"):
            with open(os.path.join(EXPERIMENTS_DIR, fname)) as f:
                cards.append(json.load(f))

    if not cards:
        print("No experiments found.")
        return

    print(f"\n{'='*60}")
    print(f"Experiment Comparison ({len(cards)} runs)")
    print(f"{'='*60}")
    print(f"{'Label':<20} {'Model':<18} {'Temp':<6} {'Exit':<6}")
    print("-" * 60)
    for c in cards:
        cfg = c["config"]
        status = c["result"]["exit_code"] if c["result"] else "?"
        print(f"{c['label']:<20} {cfg['model']:<18} {cfg['temperature']:<6} {status:<6}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prompt Experiment Runner")
    parser.add_argument("--url", default="http://localhost:3000/playwright-ui-testing-lab.html")
    parser.add_argument("--feature", default="login")
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--prompt-variant", default="standard")
    parser.add_argument("--label", default="unnamed", help="Human-readable experiment label")
    parser.add_argument("--compare", action="store_true", help="Compare all experiments")
    args = parser.parse_args()

    if args.compare:
        compare_experiments()
    else:
        run_experiment(
            args.url,
            args.feature,
            args.model,
            args.temperature,
            args.prompt_variant,
            args.label,
        )
