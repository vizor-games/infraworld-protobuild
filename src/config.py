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

from src.util import Misc
from deepdiff import DeepDiff
from pprint import pprint


class Config:
    def __init__(self, options: dict):
        self.options = options

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

    @staticmethod
    def load(path: str):
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
            yaml_config = yaml.load(stream)
            return Config(yaml_config), changed
