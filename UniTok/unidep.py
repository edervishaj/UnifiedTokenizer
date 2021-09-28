import json
import os

import numpy as np

from .unitok import UniTok
from .classify import Classify
from .vocab import VocabDepot, Vocab


class UniDep:
    def __init__(self, store_dir):
        self.store_dir = os.path.expanduser(store_dir)

        self.meta_path = os.path.join(self.store_dir, 'meta.data.json')
        self.meta_data = Classify(json.load(open(self.meta_path)))

        if self.meta_data.version != UniTok.VER:
            print('UniTok version not match, it may occur unexpected errors in loading phase!')

        self.data_path = os.path.join(self.store_dir, 'data.npy')
        self.data = np.load(self.data_path, allow_pickle=True)
        try:
            self.data = self.data.item()  # type: dict
        except Exception as err:
            print(err)

        self.id_col = self.meta_data.id_col
        self.id_vocab = self.meta_data.col_info.d[self.id_col].vocab
        self.sample_size = self.meta_data.vocab_info.d[self.id_vocab].size
        print('Loaded', self.sample_size, 'samples!')

        data_sample_size = len(self.data[self.id_col])
        if self.sample_size != data_sample_size:
            print('Resize sample size to', data_sample_size)
            self.sample_size = data_sample_size

        self.col_info = self.meta_data.col_info
        self.vocab_info = self.meta_data.vocab_info

        self.vocab_depot = VocabDepot()
        for vocab_name in self.vocab_info.d:
            self.vocab_depot.append(Vocab(name=vocab_name).load(self.store_dir))

    def is_list_col(self, col_name):
        return 'max_length' in self.col_info.d[col_name].d

    def get_max_length(self, col_name):
        if self.is_list_col(col_name):
            return self.col_info.d[col_name].max_length

    def __getitem__(self, index):
        return {col_name: self.data[col_name][index] for col_name in self.col_info.d}

    def __len__(self):
        return self.sample_size