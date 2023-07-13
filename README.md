# benchmark-action-playtest
Sandbox repo for trying out various things.

## gh-pages

The `gh-pages` site is [deployed at this address](https://willgraham01.github.io/benchmark-action-playtest/), although might not contain anything as the website build has been delegated to [another repository](#deploy-results-to-another-repo-and-trigger-website-build).

## Deploy results to another repo and trigger website build

The "profiling" workflow is triggered on pushes to main and on request.
This workflow calls the `benchmark.py` script which produces `.pyisession` files containing the profiling outputs alongside some metadata files.
These files are pushed to the `target` branch of the [`willGraham01/benchmark-action-playtest-target`](https://github.com/willGraham01/benchmark-action-playtest-target/) repository, and a `repository_dispatch` event is sent to trigger the website build in that repository.

Output files from profiling have the same filenames but different extensions to distinguish them;
- The `pyisession` file contains the `pyinstrument` profiling output.
- The `.json` file is contains the `json` output of the profiling session. This can be obtained from the `ipysession` file, and so does not need to be pushed.
- A `.stats.json` file containing metadata that we otherwise want to pass across to the website build, but which cannot be obtained from the `.pyisession` file. These are things like the commit SHA/hash, the workflow event trigger, pull request target, etc.

To work, this repository need a `PAT` token available as an `actions` secret.
Said `PAT` token needs at least read/write access to the `contents` of the target repository, as well as `metadata` read permissions (as otherwise the website rebuild cannot be triggered).
