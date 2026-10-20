"""Worker entry point. F00 has no job queue: it validates settings and idles."""

from __future__ import annotations

import argparse
import threading
from collections.abc import Sequence

from meshvera.config import Settings, load_settings_or_exit


def run_worker(
    settings: Settings,
    stop: threading.Event,
    max_polls: int | None = None,
) -> int:
    """Poll loop placeholder. Returns the number of polls performed.

    Later features replace the empty poll with lease-based job claiming.
    """
    polls = 0
    while not stop.is_set():
        polls += 1  # no jobs exist yet
        if max_polls is not None and polls >= max_polls:
            break
        stop.wait(settings.worker_poll_seconds)
    return polls


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m meshvera.worker")
    parser.add_argument("--once", action="store_true", help="poll once and exit")
    args = parser.parse_args(argv)

    settings = load_settings_or_exit()
    print(
        f"meshvera worker started (env={settings.app_env}, "
        f"llm_mode={settings.llm_mode}); no jobs yet"
    )
    stop = threading.Event()
    try:
        run_worker(settings, stop, max_polls=1 if args.once else None)
    except KeyboardInterrupt:
        stop.set()
    print("meshvera worker stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
