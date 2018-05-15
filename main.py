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
from src.dir_hasher import DirHasher
from src.util import PathConverter, Misc


def main():
    # remember time
    start_time = time.time()

    # load config
    root_dir = os.path.dirname(os.path.realpath(__file__))
    config, config_changed = Misc.load_config(os.path.abspath(PathConverter.to_absolute(root_dir, 'config.yml')))

    # then compile our matcher
    pattern = "(^.+)\\.{}$".format('|'.join(config.get('extensions', [])))
    matcher = re.compile(pattern)

    # parse CLI
    pretty_langs = [Misc.pretty_language_name(l) for l in config['languages']]
    p = argparse.ArgumentParser(description=f"Generates code from *.proto files. Supported: {', '.join(pretty_langs)}.")

    # add parse arguments from YAML (only booleans now supported)
    for k, v in config.items():
        if isinstance(k, str) and isinstance(v, bool):
            abbrev = k[0].upper()

            p.add_argument(f'-{abbrev}', f'--{k.lower()}', action='store_true',
                           help='(comments were stripped, see YAML config for details)')

    # replace config items
    parse_args = p.parse_args().__dict__
    for k, v in parse_args.items():
        # since we have only boolean params, we have to do something ONLY if it was just set to True!
        if v:
            old_color = colorama.Fore.WHITE if config[k] else colorama.Fore.RED
            new_color = colorama.Fore.WHITE

            print(f"Replacing value of '{k}' with the one provide as CLI arg. Was:",
                  old_color + str(config[k]), 'now:', new_color + 'True')

            config[k] = True

    proto_root = config['proto_root']

    if os.path.isabs(proto_root):
        abs_proto_folder = proto_root
    else:
        abs_proto_folder = os.path.join(root_dir, proto_root)

    if not os.path.isdir(abs_proto_folder):
        raise Exception(f"proto_root: {abs_proto_folder} is not a valid path")

    dh = DirHasher(config.get('force', False) or config_changed)

    codegen_args = (dh.get_changed(abs_proto_folder, matcher),
                    dh.get_matching(abs_proto_folder, matcher),
                    matcher)

    CodeGenerator(root_dir, config).gen_all(*codegen_args)

    elapsed_time = round(time.time() - start_time, 3)
    print(colorama.Fore.WHITE + f"Build done in {elapsed_time} s")


if __name__ == '__main__':
    colorama.init(True)
    main()
