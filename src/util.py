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
import json
import os
import platform
import ruamel.yaml as yaml
import zlib


class TypeCoercer:
    @staticmethod
    def assert_type_all(items: list, t: type, throwable_type: type = TypeError):
        # compare using ==, because t is't literal
        violations = list(filter(lambda i: type(i) != t, items))

        if violations:
            errors = [f"{str(v)}(got {type(v).__name__}, expected {t.__name__})" for v in violations]
            raise throwable_type(f"Got {len(violations)} type violations: {', '.join(errors)}")


class PathConverter:
    @staticmethod
    def to_relative(base_dir: str, path: str):
        if not path.startswith(base_dir):
            raise SystemError(f"path {path} is't relative to {base_dir}")

        return path[len(base_dir) + len(os.sep):]

    @staticmethod
    def to_absolute(base_dir: str, path: str):
        return os.path.join(base_dir, path)

    @staticmethod
    def all_to_relative(base_dir: str, paths: list):
        TypeCoercer.assert_type_all(paths, str)
        return [PathConverter.to_relative(base_dir, p) for p in paths]

    @staticmethod
    def all_to_absolute(base_dir: str, paths: list):
        TypeCoercer.assert_type_all(paths, str)
        return [PathConverter.to_absolute(base_dir, p) for p in paths]

    @staticmethod
    def include_suffix(path: str):
        """
        Don't know how, but c++ generator wants the exact location of .proto (file)
        (possibly due to file naming conflict resolution). Since we want completely
        authoritary way to organize folders, we need to cheat the generator
        :param path: RELATIVE path to *.proto file
        :return: suffix we need to add as -I option to protoc, there will be no suffix if
                    path is in proto_root.
        """
        if os.sep not in path:
            return ''
        else:
            sep_index = path.rfind(os.sep)
            return os.path.join(os.sep, path[:sep_index])


class Misc:
    executable_suffix = '.exe' if platform.system() == 'Windows' else ''

    @staticmethod
    def add_exec_suffix(path: str):
        return path + Misc.executable_suffix

    @staticmethod
    def make_long_dir(base_dir: str, long_dir: str):
        if not os.path.isdir(base_dir):
            raise FileNotFoundError(f'Directory {base_dir} must be an existing directory')

        # current dir shouldn't point to the same string as base_dir!
        current_dir = base_dir[:]
        for path_frag in long_dir.split(os.sep):
            current_dir += f'{os.sep}{path_frag}'
            if not os.path.isdir(current_dir):
                os.mkdir(current_dir)

    @staticmethod
    def crc_of_file(file_name: str):
        prev = 0
        with open(file_name, 'rb') as file:
            for eachLine in file:
                prev = zlib.crc32(eachLine, prev)

        return str(prev & 0xFFFFFFFF)

    @staticmethod
    def load_config(path: str):
        if not os.path.exists(path):
            raise FileExistsError(f'Config file {path} does not exist!')

        old_digest = {}
        new_digest = {path: Misc.crc_of_file(path)}

        config_digest = os.path.join(os.path.dirname(path), '.config.digest')
        if os.path.exists(config_digest):
            with open(config_digest, 'r') as cache:
                old_digest = json.load(cache)

        with open(config_digest, 'w') as cache:
            cache.write(json.dumps(new_digest, indent=4))

        # changed if digests differs
        changed = (new_digest[path] != old_digest.get(path, ''))

        with open(path, 'r') as stream:
            # must loading with version 1.1 compatibility to use boolean flags ('yes', 'on', etc.)
            return yaml.round_trip_load(stream.read(), version='1.1'), changed

    @staticmethod
    def change_ext_recursive(root_path: str, ext: str, new_ext: str):
        for root, sub, files in os.walk(root_path):
            for f in files:
                abs_path = PathConverter.to_absolute(root, f)
                full_name, extension = os.path.splitext(abs_path)

                # do [1: ] to remove a a pre-extension dot
                if extension[1:] == ext:
                    os.rename(abs_path, '.'.join([full_name, new_ext]))

    @staticmethod
    def pretty_language_name(lang: str):
        # Tries to acquire a pretty name, return 'lang' if no association found
        return {
            'cpp': 'C++',
            'csharp': 'C#',
            'js': 'JavaScript',
            'objc': 'Objective C',
            'php': 'PHP',
            'python': 'Python',
            'ruby': 'Ruby',
            'go': 'Golang',
            'java': 'Java'
        }.get(lang, lang)

    @staticmethod
    def plugin_for_lang(lang: str):
        return {
            'cpp': 'grpc_cpp_plugin',
            'csharp': 'grpc_csharp_plugin',
            'js': 'grpc_node_plugin',
            'objc': 'grpc_objective_c_plugin',
            'php': 'grpc_php_plugin',
            'python': 'grpc_python_plugin',
            'ruby': 'grpc_ruby_plugin',
            'go': 'protoc-gen-go',
            # 'java': 'protoc-gen-grpc-java'
        }.get(lang, None)

    @staticmethod
    def to_camel_case(snake_str: str):
        return ''.join(x.title() for x in (snake_str.split('_')))
