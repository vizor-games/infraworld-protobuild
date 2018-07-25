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
from src.util import PathConverter
from src.config import Config


def main():
    # remember time
    start_time = time.time()

    p = argparse.ArgumentParser(description=f"Generating from *.proto files. Enabled")
    p.add_argument('--config',
                   default=PathConverter.to_absolute(os.path.dirname(os.path.realpath(__file__)), 'config.yml')
                   )
    parse_args = p.parse_args()

    # load config
    config, config_changed = Config.load(parse_args.config)

    # display config file
    print(f'>>> Config >>>\n{str(config)}')
    proto_root = config['proto_root']

    # then compile our matcher
    pattern = "(^.+)\\.{}$".format('|'.join(config['extensions']))
    matcher = re.compile(pattern)

    root_dir = os.path.dirname(parse_args.config)

    if os.path.isabs(proto_root):
        abs_proto_folder = proto_root
    else:
        abs_proto_folder = os.path.join(root_dir, proto_root)

    if not os.path.isdir(abs_proto_folder):
        raise Exception(f"proto_root: \"{abs_proto_folder}\" is not a valid path")

    dh = DirHashCalculator(config['force'] or config_changed)

    codegen_args = (dh.get_changed(abs_proto_folder, matcher),
                    dh.get_matching(abs_proto_folder, matcher),
                    matcher)

    CodeGenerator(root_dir, config).gen_all(*codegen_args)

    elapsed_time = round(time.time() - start_time, 3)
    print(colorama.Fore.WHITE + f"Build done in {elapsed_time} s")


if __name__ == '__main__':
    colorama.init(True)
    main()
