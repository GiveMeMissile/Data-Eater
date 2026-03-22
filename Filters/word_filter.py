

class WordFilter:
    def __init__(self, words, comparison):
        self.words = words
        self.comparison = comparison

    def evaluate(self, text):
        pass

    def and_compare(self, w1, w2, text):
        if w1 in text and w2 in text:
            return True
        return False
    
    def or_compare(self, w1, w2, text):
        if w1 in text or w2 in text:
            return True
        return False
    
    