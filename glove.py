import fileprocessor
from multipledispatch import dispatch
from multiprocessing import cpu_count
import importlib
import linecache
import numpy as np
import vecmath as vm


class Glove:

    def __init__(self, glove_file, cores=cpu_count()):
        importlib.reload(fileprocessor)
        importlib.reload(vm)

        if (glove_file is not None):

            self.filename = glove_file
            self.file_processor = fileprocessor.FileProcessor(
                glove_file, cores)

            # self.load_model()

    def __call__(self, words):
        return self.get(words)

    def load_model(self):
        self.model = self.file_processor.model_from_file()
        # self.file_processor.model_to_file(self.model.copy())

    @dispatch(str)
    def get(self, word):
        return self.model[word]

    @dispatch(list)
    def get(self, words):
        return np.array([self(word) for word in words])

    def add(self, a, b):
        return np.add(self(a), self(b))

    def get_end_vector(self, a):
        return np.mean(self(a), axis=0)

    def get_feature_vector(self, a, b):

        # The average of the difference of each word vector
        # For each vector of the words in a
        # With each vector of the words in b
        return np.mean([b_vector - a_vector
                        for a_vector in self(a)
                        for b_vector in self(b)],
                       axis=0)

    def get_word_projections(self, words, feature_set_1, feature_set_2):
        """
        All params are lists of strings 

        example:
        get_word_projection(["mouse", "elephant"],["small", "little", "tiny"], ["large", "big", "huge"])

        """
        # get GloVe embeddings of words
        word_embeddings = self(words)

        # get feature subspace
        feature_vector = self.get_feature_vector(feature_set_1, feature_set_2)

        word_projections = [vm.orthogonal_projection(
            word, feature_vector) for word in word_embeddings]

        return word_projections

    def get_scores(self, words, feature_set_1, feature_set_2):
        # get GloVe embeddings of words
        word_embeddings = self(words)

        # get feature subspace
        feature_vector = self.get_feature_vector(feature_set_1, feature_set_2)

        # get projection scores
        projection_scores = [vm.projection_score(
            word, feature_vector) for word in word_embeddings]

        return projection_scores

    def get_rankings(self, words, feature_set_1, feature_set_2):
        """
        All params are lists of strings 

        Ranks words on an axis from feature 1 to feature 2

        example:
        get_rankings(["mouse", "elephant"],["small", "little", "tiny"], ["large", "big", "huge"])

        """
        # get projection scores
        projection_scores = self.get_scores(
            words, feature_set_1, feature_set_2)

        # order the words by rank
        ranks = np.argsort(projection_scores)

        return ranks

    def order_words_along_feature(self, words, feature_set_1, feature_set_2):
        """
        Return a list of words ordered along feature axis
        """
        ranks = self.get_rankings(words, feature_set_1, feature_set_2)

        return list(np.array(words)[ranks])
