import argparse
import os
from pathlib import Path

from pyinstrument import Profiler
from pyinstrument.renderers import HTMLRenderer

WORKING_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
OUTPUT_DIR = (WORKING_DIR / "outputs").resolve()


def my_function() -> None:
    print("Running this function!")
    return


def main(output_dir: Path = OUTPUT_DIR, n_reps: int = 250) -> None:
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_html_file = output_dir / "benchmark_result.html"

    p = Profiler(interval=1e-3)

    p.start()
    for i in range(n_reps):
        my_function()
    p.stop()

    session = p.last_session
    html_renderer = HTMLRenderer(show_all=False, timeline=True)

    # Write HTML file
    print(f"Writing output to: {output_html_file}", end="...", flush=True)
    with open(output_html_file, "w") as f:
        f.write(html_renderer.render(session))
    print("done")
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test script for using the github-action-benchmark tool"
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory to save outputs to.",
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
