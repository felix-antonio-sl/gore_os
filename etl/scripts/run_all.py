"""
Main ETL runner.
Executes all normalization scripts in sequence.
"""

import subprocess
import sys
from pathlib import Path
import time


SCRIPTS_DIR = Path(__file__).parent


def run_script(script_name: str) -> bool:
    """Run a single normalization script."""
    script_path = SCRIPTS_DIR / script_name

    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False

    print(f"\n{'='*60}")
    print(f"🔄 Running: {script_name}")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(SCRIPTS_DIR),
            capture_output=False,
            text=True,
        )

        if result.returncode == 0:
            print(f"✅ {script_name} completed successfully")
            return True
        else:
            print(f"❌ {script_name} failed with code {result.returncode}")
            return False

    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False


def main():
    """Run all normalization scripts."""
    print("=" * 60)
    print("🚀 GORE_OS Legacy ETL Normalization")
    print("=" * 60)

    start_time = time.time()

    # Scripts in dependency order
    scripts = [
        "normalize_convenios.py",
        "normalize_idis.py",
        "normalize_fril.py",
        "normalize_modificaciones.py",
        "normalize_partes.py",
        "normalize_progs.py",
        "normalize_250.py",
        "normalize_funcionarios.py",
        "analyze_relationships.py",
        "enrich_ipr_type.py",
        "semantic_institution_unifier.py",
        "generate_relationship_matrix.py",
    ]

    results = {}

    for script in scripts:
        results[script] = run_script(script)

    # Summary
    elapsed = time.time() - start_time
    successes = sum(1 for v in results.values() if v)
    failures = len(scripts) - successes

    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total scripts: {len(scripts)}")
    print(f"Successful: {successes}")
    print(f"Failed: {failures}")
    print(f"Time: {elapsed:.1f}s")

    for script, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {script}")

    # Output location
    output_dir = SCRIPTS_DIR.parent / "normalized"
    print(f"\n📁 Outputs: {output_dir}")

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
