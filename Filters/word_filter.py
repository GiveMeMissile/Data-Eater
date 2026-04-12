class WordFilter:
    def __init__(self, words):
        if words.lower() == "none":
            self.words = None
        elif self.check_balance(words):
            self.words = self.prepare_words(words)
        else:
            self.words = None

    def prepare_words(self, text):
        if not text or text[0] != '(' or text[-1] != ')':
            return [text]
        inner = text[1:-1]
        listed = self.parse(inner)
        return self.create_map(listed)
    
    def check_balance(self, text):
        pairs = []
        left = 0
        right = 0
        for i in range(len(text)):
            if text[i] == "(":
                pairs.append(text[i])
                left += 1
            if text[i] == ")":
                pairs.append(text[i])
                right += 1

        if not (left == right) or pairs[0] == ")" or pairs[len(pairs) - 1] == "(":
            return False
        return True

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

    def tokenize(self, s):
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
                    if len(s.split(" ")) > 1:
                        word_map["Maps"].append(self.create_map(s.split(" ")))
                        continue
                    else:
                        word_map["Maps"].append(s)
                        continue
                else:
                    word_map["Maps"].append(self.create_map(s))
                    continue
            
            if ("AND" == s or "OR" == s or "AND NOT" == s or "OR NOT" == s or s == "NOT") and (not i == 0 or not i == len(sequence) - 1):
                word_map["Operations"].append(s)
                continue
            s = s.split(" ")
            if len(s) == 1:
                word_map["Maps"].append(s[0])
            else:
                word_map["Maps"].append(self.create_map(s.split(" ")))
            if i == len(sequence) - 1:
                continue
            if sequence[i + 1] is list:
                word_map["Operations"].append("OR")
                continue
            if not ("AND" == sequence[i + 1] or "OR" == sequence[i + 1] or "AND NOT" == sequence[i + 1] or "OR NOT" == sequence[i + 1]):
                word_map["Operations"].append("OR")
    
        return word_map
    
    def check_if_valid_map(self):
        words = self.words
        if not (len(words["Operations"]) + 1 == len(words["Maps"])):
            return False
        for word in words["Maps"]:
            if not isinstance(word, dict):
                continue
            if not self.check_if_valid_map(word):
                return False
        return True

    def evaluate(self, maps, text):
        # This is some of the worst code I've ever written -_-
        text = "_" + text # Simple addition to ensure that _ can be used in not statements (this is so scuffed)
        if maps is None:
            return True

        b = self.get_boolean(maps["Maps"][0], text)
        for i in range(1, len(maps["Maps"])):
            w = maps["Maps"][i]
            operation = maps["Operations"][i - 1]
            is_not = True if (len(operation.split(" ")) == 2) else False
            if "AND" in operation:
                b = self.and_compare(b, self.get_boolean(w, text), is_not)
            else:
                b = self.or_compare(b, self.get_boolean(w, text), is_not)
        
        return b
            
    def get_boolean(self, w, text):
        if isinstance(w, dict):
            if self.evaluate(w, text):
                return True
            else:
                return False
        else:
            if w.lower() in text.lower():
                return True
            else:
                return False
            
    def and_compare(self, b1, b2, is_not):
        if is_not:
            if b1 and not b2:
                return True
            else:
                return False
        else:
            if b1 and b2:
                return True
            else:
                return False

    def or_compare(self, b1, b2, is_not):
        if is_not:
            if b1 or not b2:
                return True
            else:
                return False
        else:
            if b1 or b2:
                return True
            else:
                return False

    