import fileprocessor
from multipledispatch import dispatch
from multiprocessing import cpu_count
import importlib
import linecache
import numpy as np


class Glove:

    def __init__(self, glove_file, cores=cpu_count()):
        importlib.reload(fileprocessor)
        self.filename = glove_file
        self.file_processor = fileprocessor.FileProcessor(glove_file, cores)
        self.load_model()

    def load_model(self):
        self.model = self.file_processor.model_from_file()

    def get_word(self, word):
        return self.model[word]

    def get_words(self, words):
        return np.array([self.get_word(word) for word in words])

    @dispatch(list)
    def __call__(self, words):
        return self.get_words(words)

    @dispatch(str)
    def __call__(self, word):
        return self.get_word(word)
