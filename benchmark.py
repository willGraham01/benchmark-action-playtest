import argparse
from datetime import datetime
import json
import os
from pathlib import Path

from pyinstrument import Profiler
from pyinstrument.renderers import HTMLRenderer, JSONRenderer

from my_functions import my_function

WORKING_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
OUTPUT_DIR = (WORKING_DIR / "outputs").resolve()

HELP_STR = (
    "Produces profiling runs for a selection of models and parameters,\n"
    "writing the results in HTML and/or JSON format.\n"
    "Output names will default to the profiling timestamp if not provided."
)


def append_suffix(p: Path, ext: str) -> Path:
    """Appends (or changes) an extension to a path."""
    return (p.parent / f"{p.stem}.{ext}").resolve()


def write_metadata(fname: Path = "meta.json", **kwargs) -> None:
    metadata = {"timestamp": datetime.utcnow().strftime("%Y-%m-%d_%H%M")}
    for key, value in kwargs.items():
        if isinstance(value, Path):
            value = os.fspath(value)
        metadata[key] = value

    print(f"Writing {fname}", end="...", flush=True)
    with open(fname, "w") as f:
        json.dump(metadata, f, ensure_ascii=True)
    print("done")
    return


def current_time(formatstr: str = "%Y-%m-%d_%H%M") -> str:
    """Produces a string of the current time in the specified format."""
    return datetime.utcnow().strftime(formatstr)


def run_profiling(
    output_dir: Path = OUTPUT_DIR,
    output_name: Path = None,
    write_pyis: bool = True,
    write_stats: bool = True,
    write_html: bool = False,
    write_json: bool = False,
    n_reps: int = 25,
) -> None:
    # Create the directory that this profiling run will live in
    output_dir = output_dir / current_time("%Y/%m/%d/%H%M")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Assign output filenames
    if output_name is None:
        output_file = output_dir / "output"
    else:
        output_file = output_dir / f"{output_name.stem}"

    # Create the profiler to record the stack
    # An instance of a Profiler can be start()-ed and stop()-ped multiple times,
    # combining the recorded sessions into one at the end.
    # As such, the same profiler can be used to record the profile of multiple scripts,
    # however this may create large datafiles so using separate profilers is preferable
    p = Profiler(interval=1e-3)

    print(f"[{current_time('%H:%M:%S')}:INFO] Starting profiling runs")

    # Profile scale_run
    p.start()
    for i in range(n_reps):
        my_function()
    p.stop()

    print(f"[{current_time('%H:%M:%S')}:INFO] Profiling runs complete")

    # Fetch the recorded session: if multiple scripts are to be profiled,
    # this needs to be done after each model "run",
    # and p needs to be re-initialised before starting the next model run.
    scale_run_session = p.last_session

    # Write outputs to files
    # Renderer initialisation options:
    # show_all: removes library calls where identifiable
    # timeline: if true, samples are left in chronological order rather than total time
    if write_pyis:
        output_pyis_file = append_suffix(output_file, "pyisession")
        print(f"Writing {output_pyis_file}", end="...", flush=True)
        scale_run_session.save(output_pyis_file)
        print("done")
    if write_stats:
        output_stat_file = append_suffix(output_file, "stats.json")
        write_metadata(output_stat_file)
    if write_html:
        html_renderer = HTMLRenderer(show_all=False, timeline=False)
        output_html_file = append_suffix(output_file, "html")
        print(f"Writing {output_html_file}", end="...", flush=True)
        with open(output_html_file, "w") as f:
            f.write(html_renderer.render(scale_run_session))
        print("done")
    if write_json:
        json_renderer = JSONRenderer(show_all=False, timeline=False)
        output_json_file = append_suffix(output_file, "json")
        print(f"Writing {output_json_file}", end="...", flush=True)
        with open(output_json_file, "w") as f:
            f.write(json_renderer.render(scale_run_session))
        print("done")

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=HELP_STR)
    parser.add_argument(
        "--pyis",
        action="store_true",
        help="Write .ipysession output.",
        dest="write_pyis",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Write summary stats.",
        dest="write_stats",
    )
    parser.add_argument(
        "--html", action="store_true", help="Write HTML output.", dest="write_html"
    )
    parser.add_argument(
        "--json", action="store_true", help="Write JSON output.", dest="write_json"
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        help="Redirect the output(s) to this directory.",
        default=OUTPUT_DIR,
    )
    parser.add_argument(
        "--output_name",
        type=Path,
        help="Name to give to the output file(s). File extensions will automatically appended.",
        default=None,
    )
    parser.add_argument(
        "-n",
        type=int,
        help="Number of function calls.",
        dest="n_reps",
        default="25",
    )

    args = parser.parse_args()
    run_profiling(**vars(args))
