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
import shutil

from colorama import Fore
from src.util import TypeCoercer, Misc
from src.proto_task import ProtoTask


class CodeGenerator:
    def __init__(self, root_dir: str, config: dict):
        self.languages = config['languages']
        self.proto_root = os.path.join(root_dir, config['proto_root'])
        self.gen_root = os.path.join(root_dir, config['gen_root'])
        self.config = config

        if not os.path.isabs(self.gen_root):
            self.gen_root = os.path.join(root_dir, self.gen_root)

        if not os.path.isabs(self.gen_root):
            self.gen_root = os.path.join(root_dir, self.gen_root)

        if not os.path.isdir(self.gen_root):
            os.mkdir(self.gen_root)

        # destroy unused language folder (ones, not named in config)
        if config['wipe']:
            self.wipe_unused_language_folders()

    def wipe_unused_language_folders(self):
        for language_folder in os.listdir(self.gen_root):
            if language_folder not in self.languages:
                abs_unused_path = os.path.join(self.gen_root, language_folder)

                if os.path.isdir(abs_unused_path):
                    shutil.rmtree(abs_unused_path)
                else:
                    os.remove(abs_unused_path)

    def gen_all(self, changed_files: list, all_files: list, matcher):
        TypeCoercer.assert_type_list(changed_files, str)

        tasks = []

        if self.config['verbose']:
            files_str = f'Total num files {len(all_files)}, num changed: {len(changed_files)}'
            if self.config.get('force', False):
                files_str += ', running in FORCE mode'

            print(Fore.MAGENTA + files_str)
            [print(Fore.MAGENTA + f'    {f}, changed: {f in changed_files}') for f in all_files]

        for language in self.languages:
            # check whether we has a required plugin
            if not Misc.plugin_for_lang(language):
                print(Fore.RED + f'Unsupported desired language: {language} (have not appropriate plugin)')
                continue

            for f in all_files:
                file_has_changed = f in changed_files

                if language == 'java':
                    name, _ = os.path.splitext(f)

                    # simply reproduce snake_notation -> CamelCaseNotation
                    java_source_name = f'{Misc.to_camel_case(name)}.java'

                    # since I have no possibilities to parse out *.proto file, we have to simply check its presence
                    file_already_exist = False
                    for root, dirs, files in os.walk(os.path.join(self.gen_root, language)):
                        file_already_exist = java_source_name in files

                    file_has_changed |= not file_already_exist
                else:
                    generated_dir = os.path.join(self.gen_root, language, matcher.search(f).group(1))
                    file_has_changed |= not os.path.isdir(generated_dir)

                # generate if generated folder has been deleted OR f is in changed_files
                if file_has_changed:
                    # if we're working with java, we need a java-style path like com.foo.bar
                    # otherwise we have to generate a folder named the same as service's name
                    if language == 'java':
                        path_to_folder = language
                    else:
                        synthetic_path = matcher.search(f).group(1)
                        path_to_folder = os.path.join(language, synthetic_path)

                    # make (possibly) long path
                    Misc.make_long_dir(self.gen_root, path_to_folder)

                    # calculate an output directory
                    abs_gen_path = os.path.join(self.gen_root, path_to_folder)

                    # clean an output folder
                    shutil.rmtree(abs_gen_path)
                    os.mkdir(abs_gen_path)

                    abs_gen_path = os.path.join(self.gen_root, path_to_folder)
                    tasks.append(ProtoTask(language, abs_gen_path, f))

        print(f"Generating code ({len(tasks)} jobs to be done)...") if tasks else print('Up-to-date')

        progress = float(0)
        try:
            for t in tasks:
                t.run(self.config, self.proto_root)

                # update progress
                progress += (100.0 / float(len(tasks)))

                # print progress
                print(Fore.CYAN + f"[{str.rjust(str(int(round(progress))), 3, ' ')}%]",
                      Fore.RESET + f"{t.proto_file} for",
                      Fore.WHITE + Misc.pretty_language_name(t.lang))

        except Exception as ex:
            shutil.rmtree(self.gen_root)
            raise SystemError('An error occurred when tried to generate code: %s' % ex)

        # if some 'cpp' tasks were done, we should rename all 'cc' files into 'cpp'
        if [t for t in tasks if t.lang == 'cpp']:
            print(Fore.YELLOW + "Renaming generated C++ files from '*.cc' -> '*.hpp'")
            Misc.change_ext_recursive(os.path.join(self.gen_root, 'cpp'), 'cc', 'hpp')
