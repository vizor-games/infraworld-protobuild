
import hashlib
import json
import os

from src.util import TypeCoercer, DictDiffView


class Digest:
    config_name_tag = 'config_name'
    config_hash_tag = 'config_hash'
    files_tag = 'files'

    __create_key = object()
    __digest_dict_prototype = {
        config_name_tag: '',
        config_hash_tag: '',
        files_tag: {}
    }

    def __init__(self, data, create_key=None):
        assert (create_key == Digest.__create_key), "Digest objects must be created using Digest.load"

        self.config_name = data[Digest.config_name_tag]
        self.config_hash = data[Digest.config_hash_tag]
        self.files_hashes = data[Digest.files_tag]

    def save(self, digest_file_name: str):
        global_data = {
            Digest.config_name_tag: self.config_name,
            Digest.config_hash_tag: self.config_hash,
            Digest.files_tag: self.files_hashes
        }
        with open(digest_file_name, 'w') as digest_file:
            digest_file.write(json.dumps(global_data, indent=4))

    def update_config(self, path_to_config: str):
        self.config_name = path_to_config

        config_is_the_same = True
        if os.path.exists(path_to_config):
            config_hash = Digest.sha256_of_file(path_to_config)
            config_is_the_same = (config_hash == self.config_hash)

            # update hash
            self.config_hash = config_hash
        else:
            self.config_hash = ''

        return config_is_the_same

    def update_files(self, path_to_files: list, force: bool = False):
        """

        :param path_to_files:
        :param force:
        :return:
        """
        TypeCoercer.assert_type_list(path_to_files, str)

        files_hashes = {}
        for path_to_file in path_to_files:
            files_hashes[path_to_file] = Digest.sha256_of_file(path_to_file) if os.path.exists(path_to_file) else ''

        diff_view = DictDiffView(self.files_hashes, files_hashes)

        changed_files = []
        for path_to_file in path_to_files:
            contains = path_to_file in diff_view

            print(f"Contains {path_to_file}: {contains}")

            if contains or force:
                changed_files += path_to_file

        self.files_hashes = files_hashes
        return changed_files

    @staticmethod
    def load(digest_file_name: str):
        digest_dict = Digest.__digest_dict_prototype
        if os.path.exists(digest_file_name):
            with open(digest_file_name, 'r') as digest_file:
                try:
                    digest_dict = json.load(digest_file)
                except ValueError:
                    pass

        return Digest(digest_dict, Digest.__create_key)

    @staticmethod
    def sha256_of_file(filename, block_size=65536):
        sha256 = hashlib.sha256()
        with open(filename, 'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                sha256.update(block)
        return sha256.hexdigest()

