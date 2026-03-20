from sentence_transformers import CrossEncoder
import constants as c
import asyncio

class CrossEncoding:
    # A more advanced filter used to determine te similarity between two texts.
    # Will be used to pick out the best texts picked from the bi encoder. 
    # Acts as a final filter before the data is saved into the dataset. 

    def __init__(self, texts):
        try:
            self.model = CrossEncoder(c.CROSS_ENCODER_MODEL)
        except Exception:
            print(f"Unable to load model {c.CROSS_ENCODER_MODEL} for cross encoding, defaulting to {c.BACKUP_CROSS_ENCODER_MODEL}")
            self.model = CrossEncoder(c.BACKUP_CROSS_ENCODER_MODEL)
        self.texts = texts

    def compare(self, text):
        # Compares the inputted text with the saved texts, outputs a list of the comparisons between the texts. 

        comparison_results = []

        for c_text in self.texts:
            comparison_results.append(self.model.predict((text, c_text)))

        return comparison_results
    
    def direct_compare(self, t1, t2):
        # Directly compares two inputted texts
        return self.model.predict((t1, t2))