#!/usr/bin/env python3
"""querv

Usage:
    querv list [-p PROP] [-f FILE] [-i ID] [-m METHOD] [-a PROFILE] [-r REGION]
    querv save [-a PROFILE] [-r REGION]

    querv -h | --help
    querv --version

Any long-form option (id, file, profile, etc.) may also be specified as an environment variable of the form QUERV_$VAR
where $VAR is the option in upper case.  Specifying an environment variable takes precedence of the CLI option.

Use "save" to initialize an "output.json" file for high iteration.

Options:
    -h --help                         Show this screen.
    --version                         Show version.
    -p PROP --property=PROP           The property to pivot on.
                                      Currently implemented: ["subnets", "images", "keys", "types", "VPCs"]
                                      [default: subnets]
    -i ID --id=ID                     Identify the ec2 instance by "id" or "tag" [default: id]
    -m METHOD --method=METHOD         The method of retrieving the instances description [default: json_file]
    -f FILE --file=FILE               Use an input file [default: output.json]
    -a PROFILE --aws-profile=PROFILE  The AWS profile to use for querying [default: default]
    -r REGION --aws-region=REGION     The AWS profile to use for querying [default: us-west-2]

TODO:
    - ... so much that the main "todo" is to create this list.  There's lots of room for improvement, here.
"""


import datetime
import json
import os
import sys
from importlib.metadata import version
from typing import Dict, List, Text, Tuple, Union

import boto3
from docopt import docopt


class DateTimeEncoder(json.JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def save_snapshot(args):
    args["--method"] = "live"
    raw_data = get_data(args, trim=False)
    with open("output.json", "+w") as f:
        f.write(json.dumps(raw_data, indent=4, cls=DateTimeEncoder))
    print('WARNING: You _might_ have to find output.json under ".venv/bin"')


def get_option(opt: Text, args: Dict) -> Text:
    """
    Args:
        opt:
        args:

    Returns:

    """
    opt_env = "QUERV_{}".format(opt.upper())
    if opt_env in os.environ.keys():
        return os.environ[opt_env]
    else:
        return args["--{}".format(opt)]


# def print_result_as_list(data):
#     print("InstanceId  |  {}".format(query))
#     print("------------+------------")


def get_data(args: Dict, trim: bool = True) -> Union[Dict, List]:
    """
    Args:
        args:
        trim: Automatically descend into first level, "Reservations" (because it is known).

    Returns:
        Foobar

    Raises:
        ValueError: blah
    """
    method: Text = get_option("method", args)

    if method == "json_file":
        in_file = get_option("file", args)
        with open(in_file) as f:
            raw_data = json.load(f)
    elif method == "live":
        aws_profile = get_option("aws-profile", args)
        aws_region = get_option("aws-region", args)
        boto3.setup_default_session(profile_name=aws_profile, region_name=aws_region)
        client = boto3.client("ec2")
        raw_data = client.describe_instances()
    else:
        raise ValueError("Invalid get_data method")

    if trim:
        # All data is inside the "Reservations" key
        return raw_data["Reservations"]
    else:
        return raw_data


def get_summary(data: List, ident: Text, query: Text) -> Tuple[Dict, List]:
    """Get summary

    Args:
        data: input data
        ident: y
        query: z

    Returns:
        A tuple containing a dictionary and a list.

    """
    summary_dict = {}
    for obj in data:
        instance = obj["Instances"][0]  # 'Instances' is always a list with a length of 1

        fallback = instance["InstanceId"]
        if ident == "id":
            ec2_id = instance["InstanceId"]
        elif ident == "tag":
            results = []
            for key in instance["Tags"]:
                if key["Key"] == "Name":
                    results.append(key["Value"])
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


def pivot(summary_dict: Dict, summary_list: List) -> Text:
    """
    Args:
        summary_dict:
        summary_list:

    Returns:

    """
    s = set(val for dic in summary_list for val in dic.values())
    unique_map = {}
    for x in s:
        if x not in unique_map.keys():
            unique_map[x] = []
        for k, v in summary_dict.items():
            if x == v:
                unique_map[x].append(k)

    return json.dumps(unique_map, indent=4, sort_keys=True)


def main():
    """Main entry point for the querv CLI.
    """
    args = docopt(__doc__, version=version("querv"))
    # print(args)

    prop_dict = {
        "subnets": "SubnetId",
        "images": "ImageId",
        "keys": "KeyName",
        "types": "InstanceType",
        "VPCs": "VpcId",
    }
    query_input = get_option("property", args)
    query = prop_dict[query_input]
    ident = get_option("id", args)

    if args["save"]:
        save_snapshot(args)
        sys.exit(0)

    data = get_data(args)
    summary_dict, summary_list = get_summary(data, ident, query)

    print(pivot(summary_dict, summary_list))


if __name__ == "__main__":
    main()
