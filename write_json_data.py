import argparse
from datetime import datetime
import os
from pathlib import Path
import json

LOCATION_OF_THIS_FILE = Path(os.path.abspath(os.path.dirname(__file__)))
RECORD_DIR = (LOCATION_OF_THIS_FILE / "benchmark_records").resolve()


def record_duration_to_json(session_file: Path, record_dir: Path = RECORD_DIR):
    # Grad current timestamp for tracking purposes
    time_now = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")

    # Create output directory if it doesn't exist
    if not os.path.exists(record_dir):
        os.mkdir(record_dir)

    # Open the profiling session output
    with open(session_file, "r") as f:
        session_data = json.load(f)

    # Grab timestamp of the profiling session
    if "start_time" not in session_data.keys():
        raise RuntimeError(f"{session_file} does not record a start time!")
    else:
        timestamp = datetime.fromtimestamp(session_data["start_time"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    # Prepare output file
    data_to_dump = dict()
    data_to_dump["name"] = session_data["program"] + ": Runtime"
    data_to_dump["unit"] = "Seconds"
    data_to_dump["value"] = session_data["cpu_time"]
    data_to_dump["extra"] = f"(Writing) timestamp {time_now}"

    # Write output
    record_file = record_dir / (timestamp + ".json")
    with open(record_file, "w", encoding="utf-8") as f:
        json.dump(data_to_dump, f, ensure_ascii=True, indent=4)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extracts total CPU time from a profiling run json dump"
    )
    parser.add_argument(
        "session_file",
        type=Path,
        help="JSON file output of the profiling session",
    )
    parser.add_argument(
        "record_dir",
        type=Path,
        nargs="?",
        default=RECORD_DIR,
        action="store",
        help="Directory to save CPU duration to.",
    )

    args = parser.parse_args()
    record_duration_to_json(**vars(args))
