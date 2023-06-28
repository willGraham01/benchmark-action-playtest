import argparse
import os
from random import choice
import string
from pathlib import Path

from pyinstrument import Profiler
from pyinstrument.renderers import HTMLRenderer, JSONRenderer

WORKING_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
OUTPUT_DIR = (WORKING_DIR / "outputs").resolve()


def my_function() -> None:
    print(my_nested_function())
    return


def my_nested_function(n_chars: int = 5) -> str:
    return "".join(
        choice(string.ascii_lowercase + string.digits) for _ in range(n_chars)
    )


def main(
    html_output_dir: Path = OUTPUT_DIR,
    json_output_dir: Path = OUTPUT_DIR,
    n_reps: int = 250,
) -> None:
    if not os.path.exists(html_output_dir):
        os.mkdir(html_output_dir)
    if not os.path.exists(json_output_dir):
        os.mkdir(json_output_dir)
    html_output_file = html_output_dir / "benchmark_result.html"
    json_output_file = json_output_dir / "benchmark_result.json"

    p = Profiler(interval=1e-3)

    p.start()
    for i in range(n_reps):
        my_function()
    p.stop()

    session = p.last_session
    print(f"Session took {session.cpu_time} seconds")

    html_renderer = HTMLRenderer(show_all=False, timeline=True)
    json_renderer = JSONRenderer(show_all=False, timeline=False)

    # Write HTML file
    print(f"Writing output to: {html_output_file}", end="...", flush=True)
    with open(html_output_file, "w") as f:
        f.write(html_renderer.render(session))
    print("done")
    # Write JSON file
    print(f"Writing output to: {json_output_file}", end="...", flush=True)
    with open(json_output_file, "w") as f:
        f.write(json_renderer.render(session))
    print("done")
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test script for using the github-action-benchmark tool"
    )
    parser.add_argument(
        "html_output_dir",
        nargs="?",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory to save HTML outputs to.",
    )
    parser.add_argument(
        "json_output_dir",
        nargs="?",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory to save JSON outputs to.",
    )
    parser.add_argument(
        "-n",
        dest="n_reps",
        default=250,
        type=int,
        action="store",
        help="Number of times to run my_function.",
    )

    args = parser.parse_args()
    main(**vars(args))
