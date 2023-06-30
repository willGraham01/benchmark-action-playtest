import argparse
from datetime import datetime
import json
import os
from random import choice
import string
from pathlib import Path

from pyinstrument import Profiler
from pyinstrument.renderers import HTMLRenderer, JSONRenderer

WORKING_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
OUTPUT_DIR = (WORKING_DIR / "outputs").resolve()


def my_function() -> None:
    my_pointless_wrapper()
    print(my_nested_function())
    return


def my_nested_function(n_chars: int = 16) -> str:
    return "".join(
        choice(string.ascii_lowercase + string.digits) for _ in range(n_chars)
    )


def my_pointless_wrapper() -> None:
    for i in range(10):
        i += i
    return


def write_metadata(fname: Path = "meta.json", **kwargs) -> None:
    if fname.suffix != ".json":
        fname = fname.parent / f"{fname.stem}.json"
    print(f"Writing metadata to {fname}", end="...", flush=True)

    metadata = {"timestamp": datetime.utcnow().strftime("%Y-%m-%d_%H%M")}
    for key, value in kwargs.items():
        if isinstance(value, Path):
            value = os.fspath(value)
        metadata[key] = value

    with open(fname, "w") as f:
        json.dump(metadata, f, ensure_ascii=True)

    print("done")
    return


def main(
    html_output_file: Path = OUTPUT_DIR,
    json_output_file: Path = OUTPUT_DIR,
    n_reps: int = 250,
    metadata_file: Path = None,
) -> None:
    if not os.path.exists(html_output_file.parent):
        os.mkdir(html_output_file.parent)
    if html_output_file.suffix != ".html":
        html_output_file = html_output_file.parent / f"{html_output_file.stem}.html"
    if not os.path.exists(json_output_file.parent):
        os.mkdir(json_output_file.parent)
    if json_output_file.suffix != ".json":
        json_output_file = json_output_file.parent / f"{json_output_file.stem}.json"

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

    # Write metadata if requested
    if metadata_file is not None:
        if not os.path.exists(metadata_file.parent):
            os.mkdir(metadata_file.parent)
        if metadata_file.suffix != ".json":
            metadata_file = metadata_file.parent / f"{metadata_file.stem}.json"
        write_metadata(metadata_file, html=html_output_file, json=json_output_file)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test script for using the github-action-benchmark tool"
    )
    parser.add_argument(
        "-m",
        nargs="?",
        type=Path,
        dest="metadata_file",
        default=None,
        help="Write metadata to json file.",
    )
    parser.add_argument(
        "--html",
        nargs="?",
        type=Path,
        dest="html_output_file",
        default=OUTPUT_DIR / "out.html",
        help="File to save HTML outputs to.",
    )
    parser.add_argument(
        "--json",
        nargs="?",
        type=Path,
        dest="json_output_file",
        default=OUTPUT_DIR / "out.json",
        help="File to save JSON outputs to.",
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
