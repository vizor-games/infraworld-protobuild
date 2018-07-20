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
import os
import subprocess

from colorama import Fore
from src.util import Misc, PathConverter


class ProtoTask:
    def __init__(self, lang: str, out_dir: str, proto_file: str):
        """
        Runs protoc to generate wrapper for proto_file
        :param lang: language from list of available languages
        :param out_dir: an ABSOLUTE path to the directory where generated code will reside
        :param proto_file: a RELATIVE (to self.grpc_root) path to .proto file
        """
        self.lang = lang
        self.out_dir = out_dir
        self.proto_file = proto_file

    def run(self, config: dict, proto_root: str):
        abs_proto_file = PathConverter.to_absolute(proto_root, self.proto_file)

        if not os.path.exists(abs_proto_file):
            raise SystemError(f"{self.proto_file} does not exist in {proto_root}")

        programs_root = config['programs_root']

        if not programs_root:
            raise Exception("programs_root config variable should be defined")

        if not os.path.isdir(programs_root):
            raise Exception(f"programs_root: {programs_root} is not a directory")

        include_dir = proto_root + PathConverter.include_suffix(self.proto_file)
        path_to_proto_compiler = f"{os.path.join(programs_root, Misc.add_exec_suffix('protoc'))}"

        gen_transport = config['transport']
        options = [path_to_proto_compiler, f'-I={include_dir}']

        path_to_plugin = os.path.join(programs_root, Misc.add_exec_suffix(Misc.plugin_for_lang(self.lang)))

        if self.lang == 'go':
            options.append(f'--plugin={path_to_plugin}')

            if gen_transport:
                options.append(f'--{self.lang}_out=plugins=grpc:{self.out_dir}')
            else:
                options.append(f'--{self.lang}_out={self.out_dir}')
        else:
            options.append(f'--{self.lang}_out={self.out_dir}')

        # if we're generating transport code, we must declare a plugin and --grpc_out
        if gen_transport and (self.lang != 'go'):
            options += [
                f'--plugin=protoc-gen-grpc={path_to_plugin}',
                f'--grpc_out={self.out_dir}'
            ]

        # finally add the file to generate wrapper to
        options.append(abs_proto_file)

        if config['verbose']:
            print(Fore.MAGENTA + f">> {' '.join(options)}")

        subprocess.call(options)
