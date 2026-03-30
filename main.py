"""
main.py - Icurus Orchestrator
The self-improving AI agent that solves coding problems in real time.
"""

import io
import os
import sys
import time

# Enable Python UTF-8 mode (Windows fix for cp1252 UnicodeEncodeError)
os.environ.setdefault("PYTHONUTF8", "1")

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich import box

from scraper import fetch_problem_data
from ai_agent import generate_solution, optimize_solution
from sandbox import run_tests_in_sandbox

# ── UTF-8 safe console (prevents Windows cp1252 crashes) ─────────────────────
_utf8_out = (
    io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stdout, "buffer")
    else sys.stdout
)
console = Console(file=_utf8_out, highlight=True)

# ── Branding ──────────────────────────────────────────────────────────────────

BANNER = r"""
  ___ ____  _   _ ____  _   _ ____
 |_ _/ ___|| | | |  _ \| | | / ___|
  | | |    | | | | |_) | | | \___ \
  | | |___ | |_| |  _ <| |_| |___) |
 |___\____| \___/|_| \_\___/|____/

   S E L F - I M P R O V I N G   A G E N T
"""


# ── UI Helpers ────────────────────────────────────────────────────────────────

def print_banner():
    console.print(
        Panel(
            Text(BANNER, style="bold cyan", justify="center"),
            border_style="bright_blue",
            padding=(0, 2),
        )
    )
    console.print(
        "[dim]  Autonomous | Iterative | Self-Correcting[/dim]\n",
        justify="center",
    )


def print_problem(problem: str):
    console.print(Rule("[bold yellow]>> PROBLEM STATEMENT[/bold yellow]", style="yellow"))
    console.print(
        Panel(f"[white]{problem}[/white]", border_style="yellow", padding=(1, 2))
    )


def print_code(code: str, title: str, version: str = "v1"):
    colour = "green" if version == "v1" else "magenta"
    console.print(Rule(f"[bold {colour}]{title}[/bold {colour}]", style=colour))
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, border_style=colour, padding=(0, 1)))


def print_results(result: dict, attempt: int):
    table = Table(box=box.ROUNDED, border_style="bright_black", show_header=False)
    table.add_column("Key", style="bold dim")
    table.add_column("Value", style="bold")

    passed = result["passed"]
    status_str = (
        "[bold green]PASS  ALL TESTS PASSED[/bold green]"
        if passed
        else "[bold red]FAIL  TESTS FAILED[/bold red]"
    )

    table.add_row("Attempt", f"[cyan]#{attempt}[/cyan]")
    table.add_row("Status", status_str)

    if not passed and result.get("error_log"):
        table.add_row("Error Log", f"[red]{result['error_log'][:400]}[/red]")

    console.print(table)
    console.print()


# ── Data Source Menu ──────────────────────────────────────────────────────────

def select_data_source() -> dict:
    """Interactive menu: choose between live web scrape or manual input."""
    console.print(
        Panel(
            "[bold white]Select Data Source[/bold white]\n\n"
            "  [bold cyan][1][/bold cyan]  Live Web Scrape\n"
            "  [bold cyan][2][/bold cyan]  Manual Interactive Input",
            border_style="bright_blue",
            padding=(1, 3),
            title="[bold bright_blue]>> DATA SOURCE[/bold bright_blue]",
        )
    )

    choice = Prompt.ask(
        "[bold cyan]Your choice[/bold cyan]",
        choices=["1", "2"],
        default="1",
        console=console,
    )

    if choice == "1":
        url = Prompt.ask(
            "[bold cyan]Enter problem URL[/bold cyan]",
            default="https://codeforces.com/problemset/problem/1/A",
            console=console,
        )
        console.print()
        with console.status("[bold cyan]>> FETCHING PROBLEM DATA...[/bold cyan]", spinner="dots"):
            time.sleep(0.5)
            data = fetch_problem_data(url)
        console.print("[bold green]>> Data loaded.[/bold green]\n")
        return data

    else:  # choice == "2"
        console.print()
        prob_desc = Prompt.ask(
            "[bold cyan]Enter the problem description[/bold cyan]",
            console=console,
        )
        test_in = Prompt.ask(
            "[bold cyan]Enter a sample test input[/bold cyan]",
            console=console,
        )
        test_out = Prompt.ask(
            "[bold cyan]Enter the expected output[/bold cyan]",
            console=console,
        )
        console.print()
        return {
            "problem": prob_desc,
            "tests": [{"input": test_in, "expected": test_out}],
        }


# ── Core Pipeline ─────────────────────────────────────────────────────────────

def run_pipeline(data: dict):
    """Actor-Critic feedback loop: generate -> test -> optimise -> retest."""
    tests = data["tests"]

    print_problem(data["problem"])
    time.sleep(0.2)

    # -- Attempt 1: Generate V1 -----------------------------------------------
    with console.status("[bold green]>> GENERATING SOLUTION v1 (AI)...[/bold green]", spinner="bouncingBar"):
        time.sleep(0.6)
        code_v1 = generate_solution(data["problem"], tests=tests)

    print_code(code_v1, "GENERATED SOLUTION -- Version 1", version="v1")
    time.sleep(0.2)

    with console.status("[bold yellow]>> RUNNING V1 IN SANDBOX...[/bold yellow]", spinner="arc"):
        time.sleep(0.4)
        result_v1 = run_tests_in_sandbox(code_v1, tests)

    console.print(Rule("[bold white]SANDBOX RESULTS -- Attempt #1[/bold white]", style="white"))
    print_results(result_v1, attempt=1)

    if result_v1["passed"]:
        console.print(
            Panel(
                "[bold green]>> Icurus solved the problem on the first attempt![/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )
        return

    # -- Attempt 2: Optimise to V2 --------------------------------------------
    console.print(
        Panel(
            "[bold yellow]!! V1 failed. Engaging self-improvement loop...[/bold yellow]",
            border_style="yellow",
            padding=(0, 2),
        )
    )
    time.sleep(0.2)

    with console.status("[bold magenta]>> OPTIMISING TO SOLUTION v2 (AI)...[/bold magenta]", spinner="bouncingBall"):
        time.sleep(0.6)
        code_v2 = optimize_solution(code_v1, result_v1["error_log"])

    print_code(code_v2, "OPTIMISED SOLUTION -- Version 2", version="v2")
    time.sleep(0.2)

    with console.status("[bold yellow]>> RUNNING V2 IN SANDBOX...[/bold yellow]", spinner="arc"):
        time.sleep(0.4)
        result_v2 = run_tests_in_sandbox(code_v2, tests)

    console.print(Rule("[bold white]SANDBOX RESULTS -- Attempt #2[/bold white]", style="white"))
    print_results(result_v2, attempt=2)

    if result_v2["passed"]:
        console.print(
            Panel(
                "[bold magenta]** Icurus self-corrected and solved the problem on attempt #2![/bold magenta]",
                border_style="magenta",
                padding=(1, 2),
            )
        )
    else:
        console.print(
            Panel(
                "[bold red]XX Both attempts failed. Review the error log above.[/bold red]\n"
                "[dim]Tip: Set FEATHERLESS_API_KEY or OPENAI_API_KEY in a .env file "
                "for full AI power.[/dim]",
                border_style="red",
                padding=(1, 2),
            )
        )

    console.print(Rule(style="dim"))
    console.print("[dim]  Icurus - mission complete.[/dim]\n", justify="center")


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    print_banner()
    time.sleep(0.3)
    data = select_data_source()
    run_pipeline(data)


if __name__ == "__main__":
    main()
