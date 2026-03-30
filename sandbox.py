"""
sandbox.py - Safe Code Execution Engine for Icurus
Runs generated code in a subprocess with a strict timeout.
"""

import subprocess
import sys
import tempfile
import os


def run_tests_in_sandbox(code: str, tests: list) -> dict:
    """
    Writes `code` to a temp file, feeds each test's input via stdin,
    and checks whether the output matches the expected value.

    Returns:
        {"passed": True,  "error_log": ""}    – all tests green
        {"passed": False, "error_log": "..."}  – at least one failure
    """
    error_lines = []

    # Write code to a temporary file
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
    except Exception as exc:
        return {"passed": False, "error_log": f"Failed to write temp file: {exc}"}

    try:
        for idx, test in enumerate(tests):
            # Ensure stdin is terminated; LLM-generated `for line in sys.stdin` needs a newline
            test_input = str(test.get("input", "")) + "\n"
            expected   = str(test.get("expected", "")).strip()

            try:
                result = subprocess.run(
                    [sys.executable, tmp_path],
                    input=test_input,
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                actual = result.stdout.strip()

                if result.returncode != 0:
                    error_lines.append(
                        f"[Test {idx + 1}] Runtime error:\n{result.stderr.strip()}"
                    )
                elif actual != expected:
                    error_lines.append(
                        f"[Test {idx + 1}] FAIL – "
                        f"input={test_input!r} "
                        f"expected={expected!r} "
                        f"got={actual!r}"
                    )

            except subprocess.TimeoutExpired:
                error_lines.append(
                    f"[Test {idx + 1}] TIMEOUT – exceeded 2-second limit."
                )
            except Exception as exc:
                error_lines.append(f"[Test {idx + 1}] Execution error: {exc}")

    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    if error_lines:
        return {"passed": False, "error_log": "\n".join(error_lines)}
    return {"passed": True, "error_log": ""}
