import argparse
from datetime import datetime
import os
from pathlib import Path
import json

LOCATION_OF_THIS_FILE = Path(os.path.abspath(os.path.dirname(__file__)))
RECORD_DIR = (LOCATION_OF_THIS_FILE / "benchmark_records").resolve()


def record_duration_to_json(session_file: Path, output_file: Path = None):
    # Grad current timestamp for tracking purposes
    time_now = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")

    # Open the profiling session output
    with open(session_file, "r") as f:
        session_data = json.load(f)

    # Grab timestamp of the profiling session
    if "start_time" not in session_data.keys():
        raise RuntimeError(f"{session_file} does not record a start time!")
    else:
        timestamp = datetime.fromtimestamp(session_data["start_time"]).strftime(
            "%Y-%m-%d_%H:%M:%S"
        )

    # Prepare output file
    if output_file is None:
        output_file = RECORD_DIR / f"{timestamp}.json"
    if (
        not os.path.exists(os.path.dirname(output_file))
        and os.path.dirname(output_file) != ""
    ):
        os.mkdir(os.path.dirname(output_file))
    if output_file.suffix != ".json":
        output_file = output_file.parent / f"{output_file.name}.json"

    # Prepare output file
    data_to_dump = dict()
    data_to_dump["name"] = session_data["program"] + ": Runtime"
    data_to_dump["unit"] = "Seconds"
    data_to_dump["value"] = session_data["cpu_time"]
    data_to_dump[
        "extra"
    ] = f"(Profile timestamp) {timestamp},\n(Writing) timestamp {time_now}"

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data_to_dump, f, ensure_ascii=True, indent=4)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extracts total CPU time from a profiling run json dump"
    )
    parser.add_argument(
        "session_file",
        type=Path,
        help="JSON file output of the profiling session.",
    )
    parser.add_argument(
        "output_file",
        type=Path,
        nargs="?",
        default=None,
        action="store",
        help="Custom output file name to write result to.",
    )

    args = parser.parse_args()
    record_duration_to_json(**vars(args))
