import pandas as pd


class Finder():
    def __init__(self):
        directory='C:/Users/Asus/Desktop/GitHub Projects/projets terminés/Text Editor/assets/unigram_freq.csv' #put here the directory of the assets folder
        self.unigram_freq=pd.read_csv(open(directory,'r'))
        #self.bigram_freq=pd.read_csv(open('C:/Users/Asus/Desktop/GitHub Projects/projets à terminer/Text Editor (à terminer)/assets/bigram_freq.csv','r'))
    def startsWith(self,word):
        startsWith_word=self.unigram_freq.word.str.startswith(word,na=False)
        return(self.unigram_freq[startsWith_word].dropna().head().word.tolist())
    def startsWithKnowingBefore(self,word_before,word):
        pass

