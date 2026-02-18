import easyocr
import pandas as pd
import re

class Bwm_builder:
    def __init__(self, languages : list[str]) :
        self.languages = languages
        self.reader = easyocr.Reader(lang_list=self.languages)
        self.probabilities = []
        self.text_parts = []
        self.flatText = ""
        self.tokens = [dict]
        
        
    def readImg(self, imgPath : str = ['en']) :
        res = self.reader.readtext(imgPath)
        for (bbox, text, prob) in res:
            if (text == ""):
                continue
            self.text_parts.append(text.lower())
            self.probabilities.append(prob)
            
    def __repr__ (self) :
        return f"Bwm_builder('langs={self.languages}')"
    
    def output(self):
        print("BWM_builder")
        for i in range(len(self.text_parts)) :
            print(f"text={self.text_parts[i]}; prob={self.probabilities[i]}")

    
        """takes the broken textparts from ocr
            flattens it then splits whitespaces
            then removes every non number that is only one char
        """
    def _flattenText(self):
        for text in self.text_parts :
            self.flatText += text
            
    def _normalize_numeric_token(self, token: str) -> str:
        t = token.strip()

        # only normalize if token contains digits or number-like chars
        if not re.search(r'\d', t):
            return token

        # common OCR mistakes
        t = t.replace('o', '0')
        t = t.replace('O', '0')

        # remove invalid characters except digits and separators
        t = re.sub(r'[^0-9,.\-%]', '', t)

        # normalize multiple separators (optional refinement)
        # example: 1.890,00 stays valid

        return t
    
    def tokenize(self):
        self._flattenText()
        raw_tokens = re.split(r'\s+', self.flatText)

        for raw in raw_tokens:
            norm = self._normalize_numeric_token(raw)
            classified = self._classify_token(norm)

            self.tokens.append({
                "raw": raw,
                "normalized": norm,
                "type": classified["type"],
                "value": classified["value"]
            })

        return self.tokens

    
    def _classify_token(self, token: str) -> dict:
        t = token.lower()

        if re.fullmatch(r'atu\d{6,}', t):
            return {"type": "uid", "value": t}

        if re.fullmatch(r'\d+%', t):
            return {"type": "percent", "value": t}

        if re.fullmatch(r'\d{1,3}(?:[.,]\d{3})*[.,]\d{2}', t):
            return {"type": "money", "value": t}

        if re.fullmatch(r'\d+[.,]\d{2}', t):
            return {"type": "money", "value": t}

        if re.fullmatch(r'\d+', t):
            return {"type": "number", "value": t}

        return {"type": "text", "value": token}
    
    
    def extract_rows(self):
        rows = []
        i = 0
        n = len(self.tokens)

        while i < n:

            # look for money token pattern
            if self.tokens[i]["type"] == "money":

                # look ahead for second money token
                if i + 1 < n and self.tokens[i + 1]["type"] == "money":

                    # walk backwards to collect text
                    j = i - 1
                    text_self.tokens = []

                    while j >= 0 and self.tokens[j]["type"] == "text":
                        text_self.tokens.append(self.tokens[j]["value"])
                        j -= 1

                    text_self.tokens.reverse()

                    if text_self.tokens:
                        rows.append({
                            "product": " ".join(text_self.tokens),
                            "unit_price": self.tokens[i]["value"],
                            "total": self.tokens[i + 1]["value"]
                        })

                    i += 2
                    continue

            i += 1

        return rows




    
if __name__ == "__main__":
    builder = Bwm_builder(['de'])
    builder.readImg("tests/image.png")
    builder.tokenize()
    print(builder.tokens)