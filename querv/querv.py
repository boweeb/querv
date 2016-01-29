#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
"""querv

Usage:
  querv list [-p PROP] [-f FILE] [-i ID] [-m METHOD] [-a PROFILE]

  querv -h | --help
  querv --version

Any long-form option (id, file, profile, etc.) may also be specified as an environment variable of the form QUERV_$VAR
where $VAR is the option in upper case.  Specifying an environment variable takes precedence of the CLI option.

Options:
  -h --help                  Show this screen.
  --version                  Show version.
  -p PROP --property=PROP    The property to pivot on.
                             Currently implemented: "subnets", "images", "keys", "types" and "VPCs"[default: subnets]
  -i ID --id=ID              Identify the ec2 instance by "id" or "tag" [default: id]
  -m METHOD --method=METHOD  The method of retrieving the instances description [default: json_file]
  -f FILE --file=FILE        Use an input file [default: output.json]
  -a PROFILE --aws=PROFILE   The AWS profile to use for querying [default: default]
"""

from __future__ import unicode_literals, print_function

import os
import json
from docopt import docopt
from typing import Tuple
import boto3

__author__ = 'Jesse Butcher'
__email__ = 'boweeb@gmail.com'
__version__ = '0.1.0'


def get_option(opt: str, args: dict) -> str:
    """
    Args:
        opt:
        args:

    Returns:

    """
    opt_env = 'QUERV_{}'.format(opt.upper())
    if opt_env in os.environ.keys():
        return os.environ[opt_env]
    else:
        return args['--{}'.format(opt)]


# def print_result_as_list(data):
#     print("InstanceId  |  {}".format(query))
#     print("------------+------------")


def get_data(args: dict) -> list:
    """
    Args:
        args (dict):

    Returns:
        list: asdf

    Raises:
        ValueError: blah
    """
    method = get_option('method', args)
    """str: Method
    """

    if method == 'json_file':
        in_file = get_option('file', args)
        with open(in_file) as f:
            raw_data = json.load(f)
    elif method == 'live':
        aws_prof = get_option('aws', args)
        boto3.setup_default_session(profile_name=aws_prof)
        client = boto3.client('ec2')
        raw_data = client.describe_instances()
    else:
        raise ValueError("Invalid get_data method")

    # All data is inside the "Reservations" key
    return raw_data['Reservations']


def get_summary(data: list, ident: str, query: str) -> Tuple[dict, list]:
    """Get summary

    Args:
        data (list): input data
        ident (str): y
        query (str): z

    Returns:
        Tuple[dict, list]: A tuple containing a dictionary and a list.

    """
    summary_dict = {}
    for obj in data:
        instance = obj['Instances'][0]  # 'Instances' is always a list with a length of 1

        fallback = instance['InstanceId']
        if ident == 'id':
            ec2_id = instance['InstanceId']
        elif ident == 'tag':
            results = []
            for key in instance['Tags']:
                if key['Key'] == 'Name':
                    results.append(key['Value'])
            if len(results) != 1:
                ec2_id = fallback
            else:
                if results[0] == "":
                    ec2_id = fallback
                else:
                    ec2_id = results[0]
        else:
            raise NotImplementedError("Non-implemented value for 'ident'")
        result = instance[query]
        # print('{}  |  {}'.format(ec2_id, result))

        summary_dict[ec2_id] = result
    summary_list = []
    for record in summary_dict.keys():
        summary_list.append({record: summary_dict[record]})

    return summary_dict, summary_list


def pivot(summary_dict: dict, summary_list: list) -> str:
    """
    Args:
        summary_dict:
        summary_list:

    Returns:

    """
    s = set(val for dic in summary_list for val in dic.values())
    uniqs = {}
    for x in s:
        if x not in uniqs.keys():
            uniqs[x] = []
        for k, v in summary_dict.items():
            if x == v:
                uniqs[x].append(k)

    return json.dumps(uniqs, indent=4, sort_keys=True)


def main():
    """Main entry point for the querv CLI.
    """
    args = docopt(__doc__, version=__version__)
    # print(args)

    prop_dict = {'subnets': 'SubnetId',
                 'images': 'ImageId',
                 'keys': 'KeyName',
                 'types': 'InstanceType',
                 'VPCs': 'VpcId',
                 }
    query_input = get_option('property', args)
    query = prop_dict[query_input]
    ident = get_option('id', args)

    data = get_data(args)
    summary_dict, summary_list = get_summary(data, ident, query)

    print(pivot(summary_dict, summary_list))


if __name__ == '__main__':
    main()


# vim:fileencoding=utf-8