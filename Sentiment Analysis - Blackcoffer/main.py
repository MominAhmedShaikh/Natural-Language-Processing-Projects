from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import re
from utils import DataExtraction
from utils import DataCleaning
from utils import TextProcessing
from utils import PositiveAndNegativeFiles
from utils import Solution


if not os.path.isdir('/config/workspace/textfiles'):
    dir = os.makedirs('/config/workspace/textfiles')
path = '/config/workspace/textfiles'
input_url_path = '/config/workspace/Input.xlsx - Sheet1.csv'
input = pd.read_csv(input_url_path)


pronounRegex = re.compile(r'\b(I|we|my|ours|(?-i:us))\b',re.I)



text_list = []
title_list = []

for i,j in enumerate(input['URL_ID']):
  obj = DataExtraction(input['URL'][i],str(j))
  obj.ExtractTitleAndText()
  obj.DownloadFile(dir=path)
  text_list.append(obj.extract_text())
  title_list.append(obj.extract_title())


input['title'] = pd.DataFrame(title_list)
input['article_text'] = pd.DataFrame(text_list)


obj = DataCleaning()
stopwords = obj.decodeStopWords()
# print(input.head())
# print(len(stopwords))

stopword = [words.lower() for words in stopwords]
# print(stopword[0:5])

obj = TextProcessing(input['article_text'][0])
clean_text = obj.CleanText(stopword)
# print(clean_text)

obj = PositiveAndNegativeFiles()
negative_words,positive_words = obj.NegAndPosWord()
# print(positive_words,negative_words)


negative_score,positive_score,polarity_score,subjectivity_score,fog_index = list(),list(),list(),list(),list()
per_complex_words,avgWordsPerSent,complex_word_count,cleaned_words_count = list(),list(),list(),list()
syllable_per_word,personal_pronouns_count,avg_word_len = list(),list(),list()

for i in range(len(input['article_text'])):
  print(f'********* Generating Text Stats For Text Article Present at index {i} ***********')
  obj = TextProcessing(input['article_text'][i])
  clean_text = obj.CleanText(stopword)


  obj2 = Solution()
  neg_score,pos_score = obj2.CountPositiveAndNegative(clean_text,positive_words,negative_words)
  pol_score = (pos_score - neg_score)/((pos_score + neg_score) + 0.000001)
  sub_score = (pos_score + neg_score)/ ((len(clean_text)) + 0.000001)
  complex_words = obj2.ComplexWords(input['article_text'][i])
  fog_ind,perc,avg = obj2.AnalysisOfReadibility(input['article_text'][i]) 
  avg_word_len_count = sum([len(word) for word in clean_text])/((len(clean_text)) + 0.000001) # Added 0.000001 To Bypass ZeroDivisionError

  negative_score.append(neg_score)
  positive_score.append(pos_score)
  polarity_score.append(pol_score)
  subjectivity_score.append(sub_score)
  fog_index.append(fog_ind)
  per_complex_words.append(perc)
  avgWordsPerSent.append(avg)
  complex_word_count.append(complex_words)
  cleaned_words_count.append(len(clean_text))
  syllable_per_word.append(complex_words/((len(clean_text)) + 0.000001)) # Added 0.000001 To Bypass ZeroDivisionError
  personal_pronouns_count.append(len(pronounRegex.findall(input['article_text'][i])))
  avg_word_len.append(avg_word_len_count)


input['positive_score'] = pd.DataFrame(positive_score)
input['negative_score'] = pd.DataFrame(negative_score)
input['polarity_score'] = pd.DataFrame(polarity_score)
input['subjectivity_score'] = pd.DataFrame(subjectivity_score)
input['percentage_of_complex_words'] = pd.DataFrame(per_complex_words)
input['fog_index'] = pd.DataFrame(fog_index)
input['avg_no_words_sent'] = pd.DataFrame(avgWordsPerSent)
input['complex_words_count'] = pd.DataFrame(complex_word_count)
input['clean_words_count'] = pd.DataFrame(cleaned_words_count)
input['syllable_per_word'] = pd.DataFrame(syllable_per_word)
input['personal_pronouns'] = pd.DataFrame(personal_pronouns_count)
input['avg_word_len'] = pd.DataFrame(avg_word_len)


print(input.head())

input.to_csv('Output.csv')

