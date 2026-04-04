

class WordFilter:
    def __init__(self, words, comparison):
        self.words = self.prepare_words(words)

    def prepare_text(self, text):
        if not text or text[0] != '(' or text[-1] != ')':
            return [text]
        inner = text[1:-1]
        listed = self.parse(inner)
        return self.create_map(listed)

    def parse(self, s):
        if '(' not in s:
            return [s]
        tokens = self.tokenize(s)
        result = []
        for token in tokens:
            if token.startswith('(') and token.endswith(')'):
                result.append(self.parse(token[1:-1]))
            else:
                result.append(token)
        return result

    def tokenize(s):
        tokens = []
        i = 0
        while i < len(s):
            if s[i].isspace():
                i += 1
                continue
            if s[i] == '(':
                count = 1
                j = i + 1
                while j < len(s) and count > 0:
                    if s[j] == '(':
                        count += 1
                    elif s[j] == ')':
                        count -= 1
                    j += 1
                tokens.append(s[i:j])
                i = j
            else:
                start = i
                while i < len(s) and not s[i].isspace() and s[i] != '(':
                    i += 1
                tokens.append(s[start:i])
        return tokens

    def create_map(self, sequence):
        i = 0
        word_map = {
            "Operations": [],
            "Maps": []
        }
        for i in range(len(sequence)):
            s = sequence[i]

            if isinstance(s, list):
                if len(s) == 1:
                    s = s[0]
                    word_map["Maps"].append(self.create_map(s.split(" ")))
                    continue
                else:
                    word_map["Maps"].append(self.create_map(s))
                    continue
            
            if ("AND" == s or "OR" == s) and (not i == 0 or not i == len(sequence) - 1):
                word_map["Operations"].append(s)
                continue
            s = s.split(" ")
            if len(s) == 1:
                word_map["Maps"].append(s)
            else:
                word_map["Maps"].append(self.create_map(s.split(" ")))
            if i == len(sequence) - 1:
                continue
            if sequence[i + 1] is list:
                word_map["Operations"].append("AND")
                continue
            if not ("AND" in sequence[i + 1] or "OR" in sequence[i + 1]):
                word_map["Operations"].append("AND")
    
        return word_map

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
    
    