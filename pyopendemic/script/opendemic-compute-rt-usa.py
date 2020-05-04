import argparse
from os import path

import opendemic as od
import pandas as pd

description = 'Compute the reproduction number for USA data.'

parser = argparse.ArgumentParser(description=description)

parser.add_argument(
    '--state',
    type=str,
    metavar='[AA]',
    help='Identification code of the state. E.g. AK for Alaska. This field is '
         'ignored if `--county` is specified.'
)

parser.add_argument(
    '--county',
    type=int,
    metavar='[AABBB]',
    help='Five-digits FIPS code of the county. E.g. 36103 for Suffolk county, '
         'NY.'
)

parser.add_argument(
    '--sigma',
    type=float,
    default=0.25,
    metavar='[0, ... ]',
    help='Sigma for the Systrom model for the estimation of Rt. Default: 0.25.'
)

parser.add_argument(
    '--hdi',
    type=float,
    default=0.9,
    metavar='[0-1]',
    help='Significance level for the high density interval. Must be between 0'
         'and 1. Default: 0.9.'
)

parser.add_argument(
    '--csv',
    type=str,
    metavar='<path>',
    help='Path where the csv file with the results will be saved. If not '
         'specified, it prints to stdout.'
)

parser.add_argument(
    '-f',
    action='store_true',
    help='If specified, the output file will be overwritten.'
)

args = parser.parse_args()
if args.state is None and args.county is None:
    args = parser.parse_args(['-h'])

if args.csv is not None:
    if path.isfile(args.csv) and not args.f:
        raise FileExistsError('The specified output path is an existing file. '
                              'To overwrite it, add the `-f` argument.')

if args.sigma < 0:
    raise ValueError('Sigma must be between 0 and 1.')

data = od.data.USARegionData.fetch(state=args.state, county=args.county)

rt, low, high = od.modelling.compute_rt(data.new_cases,
                                        {'sigma': args.sigma},
                                        {'p': args.hdi})

df = pd.DataFrame({'cases': data.cases, 'new_cases': data.new_cases, 'rt': rt,
                   'low': low, 'high': high}, index=data.dates)

if args.csv is None:
    print(df)
else:
    df.to_csv(args.csv)
