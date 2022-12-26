from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
import pandas as pd
import requests
import os
import string
import re
import spacy
from textstat.textstat import textstatistics
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')


header = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}
stopwords_path = '/config/workspace/wordfiles'
lemmatizer = WordNetLemmatizer()

class DataExtraction:

  def __init__(self,url,file_name):
    self.url = url 
    self.file_name = file_name

  def ExtractTitleAndText(self):
    self.response = requests.get(self.url,headers = header)
    self.soup = BeautifulSoup(self.response.content,'html.parser')
    self.text = ''.join(data.get_text() for data in self.soup.find_all("p"))
    self.title = ''.join(titles.get_text().replace(' - Blackcoffer Insights','') for titles in self.soup.find_all("title"))
    return self.title,self.text

  def DownloadFile(self,dir):
    with open(os.path.join(dir,f'{self.file_name}.txt'),'w+') as file:
      file.write(f'{self.title}\n')
      file.writelines(self.text)
      file.close()

  def extract_title(self):
    title = ''.join(titles.get_text() for titles in self.soup.find_all("title"))
    return title.replace(' - Blackcoffer Insights','')

  def extract_text(self):
    string = ''.join(data.get_text() for data in self.soup.find_all("p"))
    return string

  


class DataCleaning:


    def decodeStopWords(self):
        stopwords = []

        for files in os.listdir(stopwords_path):
            if (files.startswith('StopWords')) and (files != 'StopWords_Currencies.txt'):
                with open(os.path.join(stopwords_path,files),'r+') as file:
                    stopwords_in_file = [*file.readlines()]
                    stopwords_in_file = pd.DataFrame(stopwords_in_file)
                    stopwords_in_file = stopwords_in_file.replace("\|.*", "", regex = True)
                    stopwords_in_list = [words.strip() for words in stopwords_in_file[0]]
                    stopwords.extend(stopwords_in_list)

            elif (files.startswith('StopWords')) and (files == 'StopWords_Currencies.txt'):
                with open(os.path.join(stopwords_path,files),'r+',encoding='latin-1') as file:
                    stopwords_in_file = [*file.readlines()]
                    stopwords_in_file = pd.DataFrame(stopwords_in_file)
                    stopwords_in_file = stopwords_in_file.replace("\|.*", "", regex = True)
                    stopwords_in_list = [words.strip() for words in stopwords_in_file[0]]
                    stopwords.extend(stopwords_in_list)
            else:
                None
        return stopwords

class TextProcessing:
  def __init__(self,text):
    self.text = text

  def CleanText(self,stopword): 
    self.punctuation = string.punctuation
    self.text = self.text.lower()   # Lower Case Text
    self.text = "".join(char for char in self.text if char not in self.punctuation) # Removing Punctuations
    self.text = re.sub(r'[0-9]', '', self.text) # Removing Numbers
    self.text = nltk.word_tokenize(self.text) # Word Tokenize
    self.text = [word for word in self.text if word not in stopword] # Removing Stopwords
    self.text = [lemmatizer.lemmatize(word) for word in self.text] # Lemmatizing

    return self.text


class PositiveAndNegativeFiles:
    def NegAndPosWord(self):
        self.negative_words = []
        self.positive_words = []

        for files in os.listdir(stopwords_path):
            if files.startswith('negative'):
                with open(os.path.join(stopwords_path,files),'r+',encoding = 'latin-1') as file:
                    self.negative_word = [*file.readlines()]
                    file.close()
            elif files.startswith('positive'):
                with open(os.path.join(stopwords_path,files),'r+',encoding = 'latin-1') as file:
                    self.positive_word = [*file.readlines()]
                    file.close()

        for word in self.negative_word:
            self.negative_words.append(word.rstrip())
        for word in self.positive_word:
            self.positive_words.append(word.rstrip())
        
        return self.negative_words , self.positive_words



class Solution:

  def __init__(self):
    ...
  
  def CountPositiveAndNegative(self,text,positive_words,negative_words):

    self.negative,self.positive = 0,0
    for word in text:
      if word in positive_words:
        self.positive += 1
      elif word in negative_words:
        self.negative += -1
      else:
        None
    return self.negative * -1 , self.positive
  
  def ComplexWords(self,text): 
    self.complex_words = 0

    for word in text:
      if word.endswith('ed') or word.endswith('es'):
        self.syllable_count = textstatistics().syllable_count(text)-1
        if self.syllable_count >= 2:
          self.complex_words += 1
      else:
        self.syllable_count = textstatistics().syllable_count(text)
        if self.syllable_count >= 2:
          self.complex_words += 1

    return self.complex_words
    
  def AnalysisOfReadibility(self,text):

    self.sentences = text.split('.')
    self.words = text.split(' ')
    self.percentage_of_complex_words = self.complex_words/len(self.words)
    self.avg_words_per_sent_len = len(self.words)/len(self.sentences)
    self.fog_index = 0.4 * (self.avg_words_per_sent_len+self.percentage_of_complex_words)

    return self.fog_index,self.percentage_of_complex_words,self.avg_words_per_sent_len

