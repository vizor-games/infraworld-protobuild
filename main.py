#
# Copyright 2018 Vizor Games LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.See the
# License for the specific language governing permissions and limitations
# under the License.
#
import time

import argparse
import colorama
import os
import re

from src.code_generator import CodeGenerator
from src.dir_hash_calculator import DirHashCalculator
from src.config import Config
from src.util import Misc


def main():
    # remember time
    start_time = time.time()

    p = argparse.ArgumentParser(description=f"Generating from *.proto files. Enabled")
    p.add_argument('--workdir', default=os.path.dirname(os.path.realpath(__file__)))
    parse_args = p.parse_args()

    working_directory = parse_args.workdir
    config_path = os.path.join(working_directory, Config.TypicalName)

    # load config
    config = Config.load(config_path)

    replaceable_options = config.get_replaceable_options()
    for k, v in replaceable_options.items():
        environ_val = os.environ.get(k, str(v).lower())

        if environ_val and replaceable_options[k] != Misc.str_to_bool(environ_val):
            replaceable_options[k] = Misc.str_to_bool(environ_val)

    config.update(replaceable_options)
    config_changed = config.is_changed()

    # display config file
    print(f'Working directory: {working_directory}')
    print(f'Config: {config_path}\n{str(config)}')
    proto_root = config['proto_root']

    # then compile our matcher
    pattern = "(^.+)\\.{}$".format('|'.join(config['extensions']))
    matcher = re.compile(pattern)

    if os.path.isabs(proto_root):
        abs_proto_folder = proto_root
    else:
        abs_proto_folder = os.path.join(working_directory, proto_root)

    if not os.path.isdir(abs_proto_folder):
        raise Exception(f"proto_root: \"{abs_proto_folder}\" is not a valid path")

    dh = DirHashCalculator(config['force'] or config_changed)

    codegen_args = (dh.get_changed(abs_proto_folder, matcher),
                    dh.get_matching(abs_proto_folder, matcher),
                    matcher)

    CodeGenerator(working_directory, config).gen_all(*codegen_args)

    elapsed_time = round(time.time() - start_time, 3)
    print(colorama.Fore.WHITE + f"Build done in {elapsed_time} s")


if __name__ == '__main__':
    colorama.init(True)
    main()
