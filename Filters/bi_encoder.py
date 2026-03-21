from sentence_transformers import SentenceTransformer
import math
import constants as c
import asyncio

class BiEncoder:
    # A Quick method to see if two sentences are similar or not.
    # Will be used to quickly filter out unrelated text from the rest of the relevant data. 

    def __init__(self, texts, filter_value):
        try:
            self.model = SentenceTransformer(c.BI_ENCODER_MODEL)
        except Exception:
            print(f"Unable to load model {c.BI_ENCODER_MODEL} for bi encoding, defaulting to {c.BACKUP_BI_ENCODER_MODEL}")
            self.model = SentenceTransformer(c.BACKUP_CROSS_ENCODER_MODEL)
        self.pythagorean = lambda x: math.sqrt(sum([x[i]**2 for i in range(len(x))]))
        self.text_vectors = self.model.encode(texts)
        self.filter = filter_value

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
    
    def evaluate_text(self, text):
        # Determines if the text should be included in the overflowed dataset, returns True of False.
        # Note: The method to which the text is judged with multiple samples is likely to change.

        similarity = self.compare(text)
        similarity = sum(similarity)/len(similarity)
        if similarity > self.filter:
            return True
        return False
    
    