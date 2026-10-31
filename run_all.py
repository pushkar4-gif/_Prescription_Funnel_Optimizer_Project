"""Rebuild everything: python run_all.py   (add --llm to parse with the LLM; needs ANTHROPIC_API_KEY)"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
llm = ["--llm"] if "--llm" in sys.argv else []
for step, extra in [("src/generate_data.py", []), ("src/run_parser.py", llm), ("src/funnel_analysis.py", []), ("src/make_figures.py", [])]:
    print(f"\n=== {step} ===", flush=True)
    subprocess.run([sys.executable, str(ROOT / step), *extra], check=True, cwd=ROOT)
