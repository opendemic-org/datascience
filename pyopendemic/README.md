# Install
Open a terminal in this folder, then switch to the wanted venv/conda environment and execute

```bash
pip install -e .
```


# Test
To run the tests, move to this folder and execute
```bash
python -m unittest
```

# Scripts
At the moment only one script is available. Once the package is installed, the
following script can be called.
```bash
$ opendemic-compute-rt-usa.py 

usage: opendemic-compute-rt-usa.py [-h] [--state [AA]] [--county [AABBB]] [--sigma [0, ...]] [--hdi [0-1]] [--csv <path>] [-f]

Compute the reproduction number for USA data.

optional arguments:
  -h, --help         show this help message and exit
  --state [AA]       Identification code of the state. E.g. AK for Alaska. This field is ignored if `--county` is specified.
  --county [AABBB]   Five-digits FIPS code of the county. E.g. 36103 for Suffolk county, NY.
  --sigma [0, ... ]  Sigma for the Systrom model for the estimation of Rt. Default: 0.25.
  --hdi [0-1]        Significance level for the high density interval. Must be between 0and 1. Default: 0.9.
  --csv <path>       Path where the csv file with the results will be saved. If not specified, it prints to stdout.
  -f                 If specified, the output file will be overwritten.

```