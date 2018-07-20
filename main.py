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
from src.dir_hasher import DirHashCalculator
from src.util import PathConverter, Misc
from src.config import Config


def main():
    # remember time
    start_time = time.time()

    # load config
    root_dir = os.path.dirname(os.path.realpath(__file__))
    config, config_changed = Config.load(PathConverter.to_absolute(root_dir, 'config.yml'))

    # then compile our matcher
    pattern = "(^.+)\\.{}$".format('|'.join(config['extensions']))
    matcher = re.compile(pattern)

    # parse CLI
    pretty_languages = [Misc.pretty_language_name(l) for l in config['languages']]
    p = argparse.ArgumentParser(description=f"Generating from *.proto files. Enabled: {', '.join(pretty_languages)}.")

    # add replaceable options into our command line parser
    rep_options = config.get_replaceable_options()

    help_message = 'Comments were stripped, see config.yml for help'
    for k, v in rep_options.items():
        p.add_argument(f'--{k.lower()}', action='store_true', default=v, help=help_message)

    # replace config items
    parse_args = p.parse_args().__dict__
    config.update(parse_args)

    # display config file
    print(f'>>> Config >>>\n{str(config)}')
    proto_root = config['proto_root']

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
