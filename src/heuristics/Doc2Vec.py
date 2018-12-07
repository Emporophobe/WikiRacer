import string

import nltk
import numpy as np
from gensim.models.doc2vec import Doc2Vec
from nltk.corpus import stopwords

from heuristics.Heuristics import AbstractHeuristic


class Doc2VecHeuristic(AbstractHeuristic):
    def __init__(self, cleaned):
        self.model = Doc2Vec.load("../models/" + ("doc2vec_cleaned" if cleaned else "doc2vec"))
        self.api = None
        self.goal_vector = None
        self.summaries = {}
        self.goal = None
        self.cleaned = cleaned

    def setup(self, api, start, goal):
        self.api = api
        goal_summary_array = self.get_summary_array(goal)
        self.goal_vector = self.model.infer_vector(doc_words=goal_summary_array, alpha=0.025, steps=20)
        self.goal = goal

    def preprocess_neighbors(self, neighbors):
        new_dict = self.get_multiple_summary_arrays(neighbors)
        self.summaries.update(new_dict)

    def calculate_heuristic(self, node):
        node_summary_array = self.get_summary_array(node)
        node_summary_vector = self.model.infer_vector(node_summary_array)
        return 0 if node == self.goal else 1 - abs(self.cos_sim(node_summary_vector, self.goal_vector))

    def get_summary_array(self, node):
        node_summary = self.summaries[node] if node in self.summaries else nltk.tokenize.word_tokenize(self.api.get_summaries([node])[node])
        if self.cleaned:
            node_summary = self.clean(node_summary)
        return node_summary

    def get_multiple_summary_arrays(self, neighbors):
        summaries = self.api.get_summaries(neighbors)
        if self.cleaned:
            new_dict = {}
            for neighbor in summaries:
                new_dict[neighbor] = self.clean(nltk.tokenize.word_tokenize(summaries[neighbor]))
            summaries = new_dict
        return summaries

    @staticmethod
    def cos_sim(a, b):
        """Takes 2 vectors a, b and returns the cosine similarity according
        to the definition of the dot product
        """
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot_product / (norm_a * norm_b)

    @staticmethod
    def clean(token_array):
        sw = set(stopwords.words('english'))
        stemmer = nltk.PorterStemmer()
        new_token_array = []
        for token in token_array:
            if token.lower() not in sw and token not in string.punctuation:
                new_token_array.append(stemmer.stem(token.lower()))
        return new_token_array
