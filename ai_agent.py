"""
ai_agent.py - The Brain of Icurus
Generates and optimises code solutions via an LLM, with a local fallback.
"""

import os
import re
from dotenv import load_dotenv

load_dotenv(override=True)  # override=True ensures .env always wins over shell env

# ── Hardcoded fallback solution (palindrome) ──────────────────────────────────
FALLBACK_CODE = '''\
def is_palindrome(s: str) -> bool:
    return s == s[::-1]

# Driver – reads from stdin so the sandbox can inject inputs
import sys
for line in sys.stdin:
    word = line.strip()
    if word:
        print(str(is_palindrome(word)))
'''

# ── Helpers ───────────────────────────────────────────────────────────────────

def _strip_markdown(text: str) -> str:
    """Remove ```python ... ``` fences from model output."""
    text = re.sub(r"```(?:python)?\s*", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()


def _get_client():
    api_key = os.getenv("FEATHERLESS_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, None
    # Strip surrounding quotes that some shells / editors add
    api_key = api_key.strip().strip('"').strip("'")
    base_url = os.getenv(
        "FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1"
    )
    model = os.getenv(
        "FEATHERLESS_MODEL",
        "Qwen/Qwen2.5-Coder-32B-Instruct",
    )
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        return client, model
    except Exception as e:
        print(f"[API CLIENT ERROR] {e}")
        return None, None


# ── Public API ────────────────────────────────────────────────────────────────

def generate_solution(problem: str, tests: list = None) -> str:
    """
    Ask the LLM for a first-pass Python solution.
    Falls back to FALLBACK_CODE if no API key or request fails.
    Accepts optional `tests` list so the prompt can show expected output format.
    """
    try:
        client, model = _get_client()
        if client is None:
            print("[API] No API key found – using fallback code.")
            return FALLBACK_CODE

        # Build an example block so the model knows the exact output format
        example_block = ""
        if tests:
            examples = "\n".join(
                f"  Input:  {t['input']}\n  Output: {t['expected']}"
                for t in tests[:3]
            )
            example_block = (
                f"\n\nIMPORTANT – your output MUST match these examples exactly "
                f"(same casing, same wording):\n{examples}"
            )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert competitive programmer.\n"
                    "OUTPUT RULES (STRICT):\n"
                    "- Return ONLY raw Python code. No markdown fences, no explanations.\n"
                    "- The script MUST read each test case from stdin, one per line, "
                    "and print exactly one result per line to stdout.\n"
                    "- Match the expected output format EXACTLY – same words, same casing.\n"
                    "- Required driver pattern:\n\n"
                    "import sys\n"
                    "for line in sys.stdin:\n"
                    "    data = line.strip()\n"
                    "    if data:\n"
                    "        print(solve(data))\n"
                ),
            },
            {
                "role": "user",
                "content": f"Solve this problem:\n\n{problem}{example_block}",
            },
        ]
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=512,
            temperature=0.2,
        )
        raw = resp.choices[0].message.content or ""
        return _strip_markdown(raw) or FALLBACK_CODE

    except Exception as e:
        print(f"[API ERROR in generate_solution] {e}")
        return FALLBACK_CODE


def optimize_solution(code: str, error: str) -> str:
    """
    Ask the LLM to fix a failing solution given its error log.
    Falls back to FALLBACK_CODE if no API key or request fails.
    """
    try:
        client, model = _get_client()
        if client is None:
            return FALLBACK_CODE

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert Python debugger.\n"
                    "OUTPUT RULES (STRICT):\n"
                    "- Return ONLY the corrected raw Python code. No markdown, no explanations.\n"
                    "- The script MUST read each test case from stdin (one per line) "
                    "and print exactly one result per line.\n"
                    "- Required driver pattern:\n\n"
                    "import sys\n"
                    "for line in sys.stdin:\n"
                    "    data = line.strip()\n"
                    "    if data:\n"
                    "        print(solve(data))\n"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"This code failed with the following error:\n\n"
                    f"CODE:\n{code}\n\n"
                    f"ERROR:\n{error}\n\n"
                    "Fix the code so all tests pass. Remember: read from stdin, print to stdout."
                ),
            },
        ]
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=512,
            temperature=0.1,
        )
        raw = resp.choices[0].message.content or ""
        return _strip_markdown(raw) or FALLBACK_CODE

    except Exception as e:
        print(f"[API ERROR in optimize_solution] {e}")
        return FALLBACK_CODE
