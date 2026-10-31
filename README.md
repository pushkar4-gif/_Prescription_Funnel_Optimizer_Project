# AI Prescription Funnel Optimizer

Parses free-text ePharmacy prescriptions into structured data with an LLM, checks the output before using it, and links the result to the order funnel to find where and why orders drop.

The data is synthetic (6,000 prescriptions and orders, Jan–Jun 2026), generated with a fixed seed. Prescription text includes OCR-style noise: typos, abbreviations (BD, TDS, 1-0-1), `O` for `0`, two items on one line, missing fields.

## How it works

1. **Parse.** `LLMParser` sends the prescription and the medicine catalogue to an LLM and asks for JSON only.
2. **Validate.** Every LLM answer is checked: valid JSON, medicine exists in the catalogue, known frequency code, sensible duration and age. If a check fails, the rule-based parser is used for that prescription and the reason is logged.
3. **Flag for review.** Prescriptions with no doctor registration number, an unmatched item, or a missing frequency or duration go to a pharmacist; the rest can be auto-approved.
4. **Analyse the funnel.** Parsed output is joined to orders in SQL (DuckDB): upload → verified → cart → paid → delivered.

## Results

Rule-based parser on all 6,000 prescriptions (run without an API key):

| Metric | Value |
|---|---|
| Medicine name F1 | 97.7% |
| Frequency accuracy | 94.8% |
| Whole prescription fully correct | 81.0% |
| Parse errors caught by review flags | 100% |
| Prescriptions safe to auto-approve | 52.9% |

Funnel findings:

- 14.1% of uploads are rejected by the pharmacist; 314 of those are for a missing doctor registration number.
- Prescriptions without a registration number deliver 39% of the time vs 59% for clean ones, and take 47 vs 17 minutes to verify.
- Asking for the registration number at upload (assumed to recover half of these rejections) adds about 16 delivered orders and ₹18.5K GMV a month at current volume.

![Funnel by parse flag](docs/figures/funnel_by_parse_flag.png)
![Parser accuracy](docs/figures/parser_accuracy.png)

## Run

```bash
pip install -r requirements.txt
python run_all.py          # rule-based parser
pytest -q
```

With the LLM parser:

```bash
pip install anthropic
export ANTHROPIC_API_KEY=...
python src/run_parser.py --llm --limit 300
python src/funnel_analysis.py && python src/make_figures.py
```

`outputs/parser_eval.json` then reports the LLM's accuracy and how often it fell back to the rules.

## Structure

```
src/generate_data.py     synthetic prescriptions, catalogue and orders
src/parser.py            LLM parser, rule parser, validation, review flags
src/run_parser.py        parses all prescriptions and scores them against ground truth
src/funnel_analysis.py   runs the SQL and sizes the fix
sql/                     funnel, parse-flag, rejection and monthly queries
outputs/                 parser results, evaluation, SQL results (CSV for Power BI)
tests/                   unit tests, including LLM fallback with a fake client
```

## Tech

Python, LLM API (Anthropic), DuckDB SQL, pandas, matplotlib, pytest, GitHub Actions.
