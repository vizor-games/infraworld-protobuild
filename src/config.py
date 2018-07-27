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
import yaml
import hashlib
import pathlib as pl

from deepdiff import DeepDiff
from pprint import pprint


class Config:
    TypicalName = 'protobuild.yml'

    def __init__(self, config_path: str, options: dict):
        self.options = options

        # !!! Now config may only reside in the working directory.
        # Change the following lines if the rule will alter
        self.working_directory = os.path.dirname(config_path)

        programs_root = options['programs_root']
        if not os.path.isabs(programs_root):
            options['programs_root'] = os.path.abspath(os.path.join(self.working_directory, programs_root))

    def __str__(self):
        return json.dumps(self.options, indent=4)

    def __getitem__(self, key):
        return self.options[key]

    def get_replaceable_options(self):
        """
        Gets all options that you can override using CLI arguments.
        :return: dict of all upper-level boolean options.
        """
        replaceable_options = {}

        # find only boolean options
        for k, v in self.options.items():
            if isinstance(v, bool):
                replaceable_options[k] = v

        return replaceable_options

    def update(self, replacement_options: dict):
        diff_options = DeepDiff(replacement_options, self.options)
        changed_values = diff_options.get('values_changed')

        if changed_values:
            print('Config replacements (provided via CLI):')
            pprint(changed_values)

        self.options.update(replacement_options)

    def hex_digest(self):
        config_hash = hashlib.sha256()
        config_hash.update(str(self).encode('utf-8'))

        return config_hash.hexdigest()

    def is_changed(self):
        old_digest = {}

        config_path = os.path.join(self.working_directory, Config.TypicalName)
        config_digest_path = os.path.join(self.working_directory, f'.{pl.Path(Config.TypicalName).stem}.digest')

        if os.path.exists(config_digest_path):
            with open(config_digest_path, 'r') as cache:
                old_digest = json.load(cache)

        new_digest = {config_path: self.hex_digest()}
        with open(config_digest_path, 'w') as cache:
            cache.write(json.dumps(new_digest, indent=4))

        # changed if digests differs
        changed = (new_digest[config_path] != old_digest.get(config_path, ''))
        return changed

    @staticmethod
    def load(path: str):
        with open(path, 'r') as stream:
            yaml_config = yaml.load(stream)
            return Config(path, yaml_config)
