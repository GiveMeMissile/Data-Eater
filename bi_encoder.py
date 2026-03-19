from sentence_transformers import SentenceTransformer
import math

MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

class BiEncoder:
    def __init__(self, texts):
        self.model = SentenceTransformer(MODEL)
        self.pythagorean = lambda x: math.sqrt(sum([x[i]**2 for i in range(len(x))]))
        self.text_vectors = self.model.encode(texts)

    def cosine_similarity(self, v1, v2):
        # Calculates the cosine similarity between two vectors of the same length

        if not (len(v1) == len(v2)):
            return None
        dot_product = sum([v1[i]*v2[i] for i in range(len(v1))])
        m1 = self.pythagorean(v1)
        m2 = self.pythagorean(v2)
        return dot_product/(m1 * m2)
    
    def compare(self, text):
        # Compares the saved text vectors with a different piece of text inputted as a parameter

        text_vector = self.model.encode(text)
        similarity = []
        for vector in self.text_vectors:
            similarity.append(self.cosine_similarity(vector, text_vector))
        
        return similarity
    
    def direct_compare(self, t1, t2):
        # Directly compares two strings together using cosine similarity

        t1_vector = self.model.encode(t1)
        t2_vector = self.model.encode(t2)

        return self.cosine_similarity(t1_vector, t2_vector)
    
    