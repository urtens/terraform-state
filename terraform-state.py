#!/usr/bin/env python

import json
from sys import exit
import argparse
from copy import deepcopy
from shutil import copyfile

parser = argparse.ArgumentParser()
parser.add_argument("--state", "-s", help="original state file")
parser.add_argument("--new-state_file", "-n", help="Where to move the module")
parser.add_argument("module", nargs="*", help="Module to move")
args = parser.parse_args()
orig_state_files = args.state
new_state_file = args.new_state_file
target_resources = args.module


def move_resource(res):
    try:
        with open(new_state_file, "r+") as nf:
            new_state = json.load(nf)
    # If the file doesn't exist we start with a new template
    except IOError:
        new_state = {
            "version": 3,
            "serial": 0,
            "lineage": "7df4bea2-b556-4c95-af25-4f58107d44c7",
            "backend": {
                "type": "local",
                "config": {},
                "hash": 6268923742653417519
            },
            "modules": [
                {
                    "path": [
                        "root"
                    ],
                    "outputs": {},
                    "resources": {},
                    "depends_on": []
                }
            ]
        }

    try:
        with open (orig_state_files, "r") as f:
            try:
                original_state = json.load(f)
            except ValueError:
                print("{} doesn't look like a proper state file".format(orig_state_files))
                exit(1)
    except IOError:
        print("Couldn't open state file")
        exit(1)

    modules = [x for x in original_state["modules"]]
    root_resources = [resource for resource in original_state["modules"][0]["resources"]]

    modified_target_state = deepcopy(original_state)
    if res in root_resources:
        moved_resource = deepcopy(original_state["modules"][0]["resources"][res])
        del modified_target_state["modules"][0]["resources"][res]
        new_state["modules"][0]["resources"][res] = moved_resource
    else:
        new_modules = []
        for m in modules:
            if res in m["path"]:
                del modified_target_state["modules"][modified_target_state["modules"].index(m)]
                new_state["modules"].append(m)

    with open(orig_state_files, 'w') as nf:
        nf.write(json.dumps(modified_target_state, indent=4))

    with open(new_state_file, 'w') as nf:
        nf.write(json.dumps(new_state, indent=4))

if __name__ == "__main__":
    for r in target_resources:
        copyfile(orig_state_files, orig_state_files + ".bak")
        print("Moving {}".format(r))
        move_resource(r)
