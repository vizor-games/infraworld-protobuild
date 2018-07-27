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
import platform
import hashlib


class DictDiffView:
    __diff_a = object()
    __diff_b = object()

    def __init__(self, a: dict, b: dict):
        self.a = a
        self.b = b

    def __contains__(self, key):
        item_a = self.a.get(key, DictDiffView.__diff_a)
        item_b = self.b.get(key, DictDiffView.__diff_b)

        return item_a == item_b


class TypeCoercer:
    @staticmethod
    def assert_type_list(items: list, t: type, throwable_type: type = TypeError):
        violations = []

        for i in items:
            type_of_i = type(i)

            if type_of_i != t:
                violations = f" > For item \"{str(i)}\" expected type \"{t.__name__}\", got \"{type_of_i.__name__}\""

        if violations:
            raise throwable_type('Got ' + str(len(violations)) + ' type violations: ' + '\n'.join(violations))

    @staticmethod
    def assert_type_map(items: dict, tk: type, tv: type, throwable_type: type = TypeError):
        violations = []
        for k, v in items.items():
            type_of_k = type(k)
            type_of_v = type(v)

            if type_of_k != tk:
                violations += f" > For key \"{str(k)}\" expected type \"{tk.__name__}\", got \"{type_of_k.__name__}\""

            if type_of_v != tv:
                violations += f" > For value \"{str(k)}\" expected type \"{tk.__name__}\", got \"{type_of_k.__name__}\""

        if violations:
            raise throwable_type('Got ' + str(len(violations)) + ' type violations: ' + '\n'.join(violations))


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
        TypeCoercer.assert_type_list(paths, str)
        return [PathConverter.to_relative(base_dir, p) for p in paths]

    @staticmethod
    def all_to_absolute(base_dir: str, paths: list):
        TypeCoercer.assert_type_list(paths, str)
        return [PathConverter.to_absolute(base_dir, p) for p in paths]

    @staticmethod
    def include_suffix(path: str):
        """
        Don't know how, but c++ generator wants the exact location of .proto (file)
        (possibly due to file naming conflict resolution). Since we want completely
        custom way to organize folders, we need to cheat the generator
        :param path: RELATIVE path to *.proto file
        :return: suffix we need to add as -I option to protoc, there will be no suffix if
                    path is in proto_root.
        """
        if os.sep in path:
            sep_index = path.rfind(os.sep)
            return os.path.join(os.sep, path[:sep_index])
        else:
            return ''


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
    def hash_of_file(file_name: str):
        hash_object = hashlib.sha256()

        with open(file_name, 'rb') as file:
            for eachLine in file:
                hash_object.update(eachLine)

        return hash_object.hexdigest()

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

    @staticmethod
    def get_binary_release_os():
        machine = platform.machine()

        if machine.endswith('64'):
            return {
                'darwin': 'Mac',
                'linux': 'Linux',
                'windows': 'Win64'
            }.get(platform.system().lower(), None)
        else:
            raise SystemError(f'Unable to operate on {machine}, 64bit operating system is required')

    @staticmethod
    def str_to_bool(input_str: str):
        return input_str.lower() == 'true'
