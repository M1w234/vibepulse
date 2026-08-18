#!/usr/bin/env python3
"""Install VibePulse tokenserver as a per-user macOS LaunchAgent."""

from __future__ import annotations

import argparse
import os
import plistlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


LABEL = "se.torget.tokenserver"
DEFAULT_PORT = 8737


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--github-repo")
    parser.add_argument("--claude-plan", choices=("pro", "max5x", "max20x"))
    parser.add_argument("--codex-plan", choices=("plus", "pro"))
    parser.add_argument("--plan", action="append", default=[], metavar="PROVIDER=USD")
    parser.add_argument("--interactions", action="store_true")
    parser.add_argument("--interaction-detail", action="store_true")
    parser.add_argument("--python", dest="python_path", type=Path)
    parser.add_argument("--dry-run", action="store_true",
                        help="print the generated plist; change nothing")
    parser.add_argument("--force", action="store_true",
                        help="replace a different existing plist (keeps .bak)")
    return parser


def _program_arguments(args: argparse.Namespace, python_path: Path,
                       script_path: Path) -> list[str]:
    values = [str(python_path), "-u", str(script_path), "--port", str(args.port)]
    for flag, value in (("--github-repo", args.github_repo),
                        ("--claude-plan", args.claude_plan),
                        ("--codex-plan", args.codex_plan)):
        if value:
            values.extend((flag, value))
    for plan in args.plan:
        values.extend(("--plan", plan))
    if args.interactions:
        values.append("--interactions")
    if args.interaction_detail:
        values.append("--interaction-detail")
    return values


def build_plist(args: argparse.Namespace, *, python_path: Path,
                tokenserver_dir: Path, home: Path) -> dict[str, object]:
    log_path = home / "Library" / "Logs" / "vibepulse-tokenserver.log"
    return {
        "Label": LABEL,
        "ProgramArguments": _program_arguments(
            args, python_path, tokenserver_dir / "tokenserver.py"),
        "WorkingDirectory": str(tokenserver_dir),
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 30,
        "StandardOutPath": str(log_path),
        "StandardErrorPath": str(log_path),
    }


def _local_hostname() -> str:
    try:
        result = subprocess.run(
            ("/usr/sbin/scutil", "--get", "LocalHostName"),
            check=True, capture_output=True, text=True,
        )
        value = result.stdout.strip()
        if value:
            return value
    except (OSError, subprocess.CalledProcessError):
        pass
    return socket.gethostname().removesuffix(".local").split(".", 1)[0]


def _write_plist(path: Path, content: bytes, *, force: bool) -> None:
    if path.exists():
        current = path.read_bytes()
        if current != content and not force:
            raise SystemExit(
                f"{path} already exists with different settings; inspect it, "
                "then rerun with --force to replace it (a .bak is kept).")
        if current != content:
            shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        tmp.write(content)
        temp_path = Path(tmp.name)
    temp_path.chmod(0o644)
    os.replace(temp_path, path)


def _launch(path: Path) -> None:
    domain = f"gui/{os.getuid()}"
    subprocess.run(("/bin/launchctl", "bootout", f"{domain}/{LABEL}"),
                   check=False, capture_output=True)
    subprocess.run(("/bin/launchctl", "bootstrap", domain, str(path)),
                   check=True)
    subprocess.run(("/bin/launchctl", "kickstart", "-k", f"{domain}/{LABEL}"),
                   check=True)


def _wait_for_health(port: int, timeout_s: float = 30.0) -> None:
    deadline = time.monotonic() + timeout_s
    url = f"http://127.0.0.1:{port}/"
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status == 200:
                    return
        except Exception as exc:  # bounded retry; report the final cause
            last_error = exc
        time.sleep(0.5)
    raise RuntimeError(f"LaunchAgent did not answer {url}: {last_error}")


def main(argv: list[str] | None = None) -> int:
    if sys.platform != "darwin":
        raise SystemExit("This installer is for macOS only.")
    args = _parser().parse_args(argv)
    if args.interaction_detail and not args.interactions:
        raise SystemExit("--interaction-detail requires --interactions")

    tokenserver_dir = Path(__file__).resolve().parent
    home = Path.home()
    python_path = (args.python_path or Path(sys.executable)).resolve()
    if not python_path.is_file():
        raise SystemExit(f"Python executable not found: {python_path}")
    if not (tokenserver_dir / "tokenserver.py").is_file():
        raise SystemExit(f"tokenserver.py not found in {tokenserver_dir}")

    payload = plistlib.dumps(build_plist(
        args, python_path=python_path, tokenserver_dir=tokenserver_dir,
        home=home), sort_keys=False)
    if args.dry_run:
        sys.stdout.buffer.write(payload)
        return 0

    (home / "Library" / "Logs").mkdir(parents=True, exist_ok=True)
    plist_path = home / "Library" / "LaunchAgents" / f"{LABEL}.plist"
    _write_plist(plist_path, payload, force=args.force)
    _launch(plist_path)
    _wait_for_health(args.port)

    host = _local_hostname()
    print(f"VibePulse tokenserver is running: http://{host}.local:{args.port}")
    print("Use this in secrets.h:")
    print(f'#define TK_VIBEPULSE_BASE_URL "http://{host}.local:{args.port}"')
    print(f"Log: {home / 'Library' / 'Logs' / 'vibepulse-tokenserver.log'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
