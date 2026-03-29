"""
Icurus – Self-Improving Agent
Member 4 (Orchestrator): CLI pipeline with Rich terminal UI.

Swap the MOCK functions below with real imports from team modules:

    from member1_brightdata   import fetch_problem          # replaces mock_fetch_data
    from member2_featherless  import generate_code          # replaces mock_generate_code
    from member2_featherless  import optimize_code          # replaces mock_optimize_code
    from member3_sandbox      import run_code               # replaces mock_run_sandbox
"""

import time
import random
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich import box

console = Console()

# ──────────────────────────────────────────────────────────────────────────────
#  MOCK LAYER  (Members 1-3 will replace these with real implementations)
# ──────────────────────────────────────────────────────────────────────────────

def mock_fetch_data(problem_url: str) -> dict:
    """
    [Member 1 – BrightData]
    Returns a dict with 'title', 'description', and 'examples'.
    """
    time.sleep(1.2)
    return {
        "title": "Two Sum",
        "description": (
            "Given an array of integers nums and an integer target, "
            "return indices of the two numbers such that they add up to target."
        ),
        "examples": [
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"},
            {"input": "nums = [3,2,4], target = 6",     "output": "[1,2]"},
        ],
    }


def mock_generate_code(problem: dict, attempt: int = 1) -> str:
    """
    [Member 2 – Featherless AI]
    Generates an initial Python solution for the problem.
    Returns a string of Python source code.
    """
    time.sleep(1.5)
    if attempt == 1:
        # Deliberately buggy first draft so the loop can kick in
        return (
            "def solution(nums, target):\n"
            "    for i, n in enumerate(nums):\n"
            "        complement = target - n\n"
            "        if complement in nums:\n"
            "            return [i, nums.index(complement)]  # BUG: may return same index\n"
        )
    # Second draft is correct
    return (
        "def solution(nums, target):\n"
        "    seen = {}\n"
        "    for i, n in enumerate(nums):\n"
        "        complement = target - n\n"
        "        if complement in seen:\n"
        "            return [seen[complement], i]\n"
        "        seen[n] = i\n"
    )


def mock_run_sandbox(code: str, examples: list) -> tuple[bool, str]:
    """
    [Member 3 – Subprocess Sandbox]
    Executes code against examples.
    Returns (passed: bool, error_log: str).
    """
    time.sleep(0.8)
    # Simulate: first attempt always has a bug
    if "seen" not in code:
        return (
            False,
            "AssertionError on example 2: expected [1,2] but got [0,0]\n"
            "Hint: the naive lookup may return the same index twice.",
        )
    # Correct solution passes all tests
    return (True, "All test cases passed ✓")


def mock_optimize_code(code: str, error_log: str, problem: dict) -> str:
    """
    [Member 2 – Featherless AI optimizer]
    Given the failing code + error log, returns an improved version.
    """
    time.sleep(1.5)
    return mock_generate_code(problem, attempt=2)


# ──────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _header():
    title = Text("⚡  I C U R U S  ⚡", justify="center")
    title.stylize("bold bright_cyan")
    subtitle = Text("Self-Improving Competitive Programming Agent", justify="center")
    subtitle.stylize("dim white")
    console.print()
    console.print(Panel.fit(
        title + "\n" + subtitle,
        border_style="bright_blue",
        box=box.DOUBLE_EDGE,
        padding=(1, 6),
    ))
    console.print()


def _step(icon: str, label: str, style: str = "bright_white"):
    console.print(f"  [bold {style}]{icon}  {label}[/bold {style}]")


def _code_panel(code: str, title: str = "Generated Code"):
    console.print(Panel(
        code.strip(),
        title=f"[bold green]{title}[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))


def _error_panel(error_log: str):
    console.print(Panel(
        error_log.strip(),
        title="[bold red]❌  Sandbox Error Log[/bold red]",
        border_style="red",
        padding=(1, 2),
    ))


def _success_panel(iteration: int):
    msg = Text(f"✅  Solution verified and passing on iteration {iteration}!", justify="center")
    msg.stylize("bold bright_green")
    console.print(Panel(msg, border_style="green", padding=(1, 4)))


def _failure_panel():
    msg = Text("💀  Maximum iterations reached. Solution still failing.", justify="center")
    msg.stylize("bold red")
    console.print(Panel(msg, border_style="red", padding=(1, 4)))


# ──────────────────────────────────────────────────────────────────────────────
#  CORE PIPELINE
# ──────────────────────────────────────────────────────────────────────────────

MAX_ITERATIONS = 3
PROBLEM_URL    = "https://leetcode.com/problems/two-sum/"   # swap for real URL


def run_pipeline(problem_url: str = PROBLEM_URL):
    start = time.time()
    _header()

    # ── Step 1: Fetch problem ─────────────────────────────────────────────────
    console.print(Rule("[bold bright_blue] PHASE 1 · FETCH [/bold bright_blue]", style="bright_blue"))
    with console.status("[bold cyan]🌐  Fetching problem data via BrightData…[/bold cyan]", spinner="dots"):
        problem = mock_fetch_data(problem_url)
    _step("📄", f"Problem loaded: [bold yellow]{problem['title']}[/bold yellow]", "cyan")
    console.print()

    # ── Step 2: Draft V1 ──────────────────────────────────────────────────────
    console.print(Rule("[bold bright_blue] PHASE 2 · DRAFT V1 [/bold bright_blue]", style="bright_blue"))
    with console.status("[bold cyan]🤖  Featherless AI drafting initial solution…[/bold cyan]", spinner="arc"):
        code = mock_generate_code(problem, attempt=1)
    _step("✏️", "Draft V1 generated", "cyan")
    _code_panel(code, title="Draft V1")
    console.print()

    # ── Feedback Loop ─────────────────────────────────────────────────────────
    console.print(Rule("[bold bright_blue] PHASE 3 · TEST & REFINE LOOP [/bold bright_blue]", style="bright_blue"))
    passed    = False
    error_log = ""

    for iteration in range(1, MAX_ITERATIONS + 1):
        console.print(f"\n  [bold bright_magenta]🔁  Iteration {iteration} / {MAX_ITERATIONS}[/bold bright_magenta]")

        # Test in sandbox
        with console.status(f"[bold cyan]🧪  Running sandbox tests (iter {iteration})…[/bold cyan]", spinner="bouncingBar"):
            passed, error_log = mock_run_sandbox(code, problem["examples"])

        if passed:
            console.print(f"  [bold green]✔  Tests PASSED on iteration {iteration}[/bold green]")
            console.print()
            _success_panel(iteration)
            break

        # Failed – show error and optimize
        _step("❌", f"Tests FAILED on iteration {iteration}", "red")
        _error_panel(error_log)

        if iteration < MAX_ITERATIONS:
            _step("⚙️", "Sending error log to Featherless AI optimizer…", "yellow")
            with console.status("[bold yellow]🔧  Optimizing solution…[/bold yellow]", spinner="dots2"):
                code = mock_optimize_code(code, error_log, problem)
            _code_panel(code, title=f"Optimized Draft (iter {iteration + 1})")
        else:
            console.print()
            _failure_panel()

    # ── Summary ───────────────────────────────────────────────────────────────
    elapsed = time.time() - start
    console.print()
    console.print(Rule("[bold bright_blue] SUMMARY [/bold bright_blue]", style="bright_blue"))
    status_text = "[bold green]PASSED ✅[/bold green]" if passed else "[bold red]FAILED ❌[/bold red]"
    console.print(f"  Problem   : [bold yellow]{problem['title']}[/bold yellow]")
    console.print(f"  Status    : {status_text}")
    console.print(f"  Elapsed   : [bold]{elapsed:.1f}s[/bold] (limit: 60 s)")
    console.print()


if __name__ == "__main__":
    run_pipeline()
