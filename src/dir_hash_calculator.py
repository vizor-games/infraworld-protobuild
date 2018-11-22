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

from src.util import PathConverter, Misc


class DirHashCalculator:
    def __init__(self, force: bool = False):
        self.force = force

    @staticmethod
    def load_digest(config_file: str):
        if not os.path.exists(config_file):
            return {}

        with open(config_file) as cache:
            return json.load(cache)

    @staticmethod
    def save_digest(base_dir: str, config: dict):
        config_file = os.path.join(base_dir, '.dir.digest')

        with open(config_file, 'w') as cache:
            cache.write(json.dumps(config, indent=4))

    @staticmethod
    def get_matching(base_dir, matcher):
        matching = []

        for root, sub, files in os.walk(base_dir):
            for f in files:
                if matcher.match(f):
                    abs_path = PathConverter.to_absolute(root, f)
                    relative_path = abs_path[len(base_dir) + len(os.sep):]

                    matching.append(relative_path)

        return matching

    def get_changed(self, base_dir, matcher):
        digest_path = os.path.join(base_dir, '.dir.digest')

        old_digest = DirHashCalculator.load_digest(digest_path)
        new_digest = {}

        changed = []
        for matching in DirHashCalculator.get_matching(base_dir, matcher):
            new_hash = Misc.hash_of_file(os.path.join(base_dir, matching))
            new_digest[matching] = new_hash

            if new_hash != old_digest.get(matching, '') or self.force:
                changed.append(matching)

        return changed, new_digest
