from sentence_transformers import CrossEncoder

MODEL = 'cross-encoder/stsb-roberta-base'

class CrossEncoding:
    # A more advanced filter used to determine te similarity between two texts.
    # Will be used to pick out the best texts picked from the bi encoder. 
    # Acts as a final filter before the data is saved into the dataset. 

    def __init__(self, texts):
        self.model = CrossEncoder(MODEL)
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