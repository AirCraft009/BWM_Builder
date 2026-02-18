import easyocr
import polars as pl

class Bwm_builder:
    def __init__(self, languages : list[str]) :
        self.languages = languages
        self.reader = easyocr.Reader(lang_list=self.languages)
        self.probabilities = []
        self.text_parts = []
        
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
    
    def parseSelf(self):
        pass
    
    
if __name__ == "__main__":
    builder = Bwm_builder(['en'])
    builder.readImg("tests/image.png")
    builder.output()