# Clean Code Bot

CLI tool that sends source files to an LLM (OpenAI or Groq) and returns refactored code, an explanation of changes, and a summary of issues—guided by structured prompts and input sanitization.

## Requirements

- Python 3.10+
- An API key: **OpenAI** (`OPENAI_API_KEY`) and/or **Groq** (`GROQ_API_KEY`)

## Setup

```bash
cd clean_code_bot
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### API keys

Create a `.env` file in this directory (do **not** commit it; it is listed in `.gitignore`):

```env
# Default provider is OpenAI if LLM_PROVIDER is unset
OPENAI_API_KEY=sk-...

# Optional overrides
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4o-mini
# LLM_MAX_TOKENS=16384
```

For Groq:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk-...
# LLM_MODEL=llama-3.3-70b-versatile
```

Run commands from this directory so `python-dotenv` loads `.env`.

## Usage

```bash
python cli.py path/to/file.py
python cli.py path/to/file.py -o cleaned.py --explain
python cli.py path/to/file.py --provider groq --model llama-3.3-70b-versatile
```

- **`--output` / `-o`**: write refactored code to a file (optional).
- **`--explain`**: print a longer chain-of-thought section from the model.
- **`--provider`**: `openai` or `groq` (default: env `LLM_PROVIDER` or `openai`).
- **`--model`**: model name (default: env `LLM_MODEL` or provider default).
- **`--max-bytes`**: cap input size after UTF-8 encoding (default: 200000).

Example with the bundled sample:

```bash
python cli.py examples/before/sample.py -o /tmp/sample_clean.py --explain
```

## How to test

### 1. Smoke test (no API)

Check that the CLI loads:

```bash
python cli.py --help
```

### 2. Automated tests (no API, no network)

Install dev dependencies and run pytest from the project root:

```bash
pip install -r requirements-dev.txt
pytest
```

This covers the **sanitizer** (injection-style phrases, size limits) and **response parsing** (JSON, optional markdown fences).

The preferred response shape is **small JSON (metadata only)** plus **`---BEGIN_REFACTORED_CODE---` … `---END_REFACTORED_CODE---`** around the full file. That avoids huge Base64 blobs inside JSON (which can hit output token limits and truncate mid-string). Legacy single-JSON responses with `refactored_code` (plain or Base64) still parse.

### 3. End-to-end test (requires API key)

With `.env` or exported keys:

```bash
python cli.py examples/before/sample.py
```

You should see printed sections for issues summary and explanation, and refactored code (or use `-o` to write only the code to a file while still printing the narrative sections).

## Project layout

| Path | Role |
|------|------|
| `cli.py` | CLI entry point |
| `llm/` | LLM client and prompts |
| `core/` | Sanitizer, analyzer, response parsing |
| `utils/` | File read/write |
| `examples/before/` | Messy sample input |
| `examples/after/` | Illustrative refactored style (reference only) |
| `tests/` | Pytest suite |

## License

Add a license file if you publish this repository publicly.
