"""
run_all.py — Part C Stress Test Runner
=======================================
Runs all 5 stress test scenarios sequentially.
Usage:  poetry run python src/run_all.py [1|2|3|4|5|all]

Examples:
  poetry run python src/run_all.py        # runs all scenarios
  poetry run python src/run_all.py 1      # runs only Scenario 1
  poetry run python src/run_all.py 2 3    # runs Scenarios 2 and 3
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import scenario_1_batch
import scenario_2_schema_drift
import scenario_3_dirty_data
import scenario_4_apps_updated
import scenario_5_sentiment

SCENARIOS = {
    "1": ("New Reviews Batch", scenario_1_batch.run),
    "2": ("Schema Drift", scenario_2_schema_drift.run),
    "3": ("Dirty and Inconsistent Data", scenario_3_dirty_data.run),
    "4": ("Updated Apps Metadata", scenario_4_apps_updated.run),
    "5": ("New Business Logic", scenario_5_sentiment.run),
}


def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else ["all"]

    if args == ["all"]:
        to_run = list(SCENARIOS.keys())
    else:
        to_run = [a for a in args if a in SCENARIOS]
        unknown = [a for a in args if a not in SCENARIOS]
        if unknown:
            print(f"[!] Unknown scenario(s): {unknown}. Valid: 1-5 or 'all'")

    print("\n" + "=" * 60)
    print(f"   PART C — STRESS TESTING PIPELINE")
    print(f"   Running scenarios: {', '.join(to_run)}")
    print("=" * 60)

    for key in to_run:
        name, fn = SCENARIOS[key]
        print(f"\n{'─'*60}")
        print(f"  [{key}/5] {name}")
        print(f"{'─'*60}")
        try:
            fn()
        except Exception as e:
            print(f"\n  [ERROR] Scenario {key} failed: {e}")

    print("\n" + "=" * 60)
    print("   All done. Outputs saved to: part C/output/")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
