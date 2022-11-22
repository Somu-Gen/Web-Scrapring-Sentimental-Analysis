#------------------Webscraping----------------

import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize, RegexpTokenizer, sent_tokenize
from nltk.corpus import stopwords
import re
import pandas as pd


df = pd.read_excel('Input.xlsx')

lst = list(df.URL)
#print(lst)

dic = dict(df.URL_ID)

for i in range(len(lst)):
    # print('URL_ID:',dic[i], "URL:",lst[i])
    file = open(f'Scrape_text_files/{dic[i]}.txt', 'w', encoding="utf-8")
    URL = lst[i]

    headers = {'User-Agent': ''}

    r = requests.request('GET', URL, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')

    url_id = dic[i]
    try:
        Title = soup.title.text

    except Exception as e:
        Title = None

    try:
        Text = soup.find('div', class_='td-post-content').text
    except Exception as e:
        Text = " "

    # print(soup.title.text)

    file.write(Title)
    file.write(Text)

    file.close()

##------------------ StopWords-------------------------##

sw_auditor = open(r'StopWords\StopWords_Auditor.txt','r')
sw_currencies = open(r'StopWords\StopWords_Currencies.txt','r')
sw_dates = open(r'StopWords\StopWords_DatesandNumbers.txt','r')
sw_generic = open(r'StopWords\StopWords_Generic.txt','r')
sw_genericlong = open(r'StopWords\StopWords_GenericLong.txt','r')
sw_geo = open(r'StopWords\StopWords_Geographic.txt','r')
sw_names = open(r'StopWords\StopWords_Names.txt', 'r')

lts = [sw_auditor,sw_currencies,sw_dates,sw_generic,sw_genericlong,sw_geo,sw_names]

d_currenices=[]
d_auditor=[]
d_dates =[]
d_generic = []
d_genericlong =[]
d_geo=[]
d_names=[]
dlist = [d_auditor,d_currenices,d_dates,d_generic,d_genericlong,d_geo,d_names]

for i in range(0,len(lts)):
  lines = lts[i].readlines()
  for j in lines:
    d_currenices.append(j.split('|')[0].rstrip())


# Adding the given StopWords to actual in-built stopwords &
# importing the list of StopWords that are created in given_stop_word.py
en_stopwords = stopwords.words('english')

#converging all the given StopWords into a list
cnew_stopwords = d_auditor+d_dates+d_generic+d_genericlong+d_geo+d_names+d_currenices

new_stopwords=list(set(cnew_stopwords))

# new nltk updated stopwords
new_stopwords.extend(en_stopwords)
#print(len(new_stopwords))

##---------------------positive_negative words---------------------##
#module used: nltk word tokenizer

#Here we will go through positive & negative text files & clean them and convert into repective lists

#Opening text files using open method
file_positive = open("MasterDictionary/positive-words.txt","r")
file_negative = open("MasterDictionary/negative-words.txt","r")

# Creating a function to tokenize the text file data & convert into list

def positive_negative(f):
    #read the data from .txt files
    data = list(set(word_tokenize(f.read())))

    return data

positive_list =positive_negative(file_positive)
#print('Old_p',len(positive_list))

negative_list =positive_negative(file_negative)
#print('old_neg:',len(negative_list))


# Checking for stop words in positive and negative lists and removing words that already exists in StopWords(new_stopwords)
def pn(s):
    k = []
    for w in s:
        if w not in new_stopwords:
            k.append(w)
    return k

positive_words = pn(positive_list)
#print('new-p',len(positive_words))


negative_words =pn(negative_list)
#print('new-n',len(negative_words))

##-----------------------Performing Sentimental Analysis------------------##

"""modules used : re, pandas, RegexTokenizer, sent_tokenize"""


#lmkt empty list is created to append the output values list that are calculated from each text file
lmkt =[]

# This for-loop goes through every text file and perform sentimental analysis
for i in range(37,151):
    file= f'Scrape_text_files/{i}.txt'

    # reading text file using open()
    text = open(file, "r", encoding="utf-8")
    data = str(text.read())
    #print(data)


    tokenizer = RegexpTokenizer(r"\w+")
    lst = tokenizer.tokenize(data)
    # print(' '.join(lst))
    text.close()
#################
    # Sentence Tokenization
    text = open(file, "r", encoding="utf-8")

    # Sentence tokenization
    sentence_data = sent_tokenize(str(text.read()))


    def words_per_sentence(st):

        cou_nt = 0
        for i in st:
            tokenizer = RegexpTokenizer(r"\w+")
            lst = tokenizer.tokenize(i)

            # print('lst =',lst)

            cou_nt = cou_nt + len(lst)

            # we are counting It's as 2 words(It is)

        return cou_nt


    total_number_of_words = words_per_sentence(sentence_data)
###########################################
    # Function to remove stopwords from text
    def remove_stopwords(s):
        c_t = []
        for w in s:
            if w not in new_stopwords:
                c_t.append(w)

        return c_t


    clean_test = remove_stopwords(lst)


    # print('clean_test',len(clean_test),clean_test)

    # postive score function
    def positive_sc(t):
        n = 0
        for w in t:
            if w in positive_words:
                n += 1
        return n


    # negative score function
    def negative_sc(t):
        n = 0
        for w in t:
            if w in negative_words:
                n += 1
        return n


    # Positive score
    Positive_Score = positive_sc(clean_test)
    # print('Positive_Score = ',Positive_Score)

    # Negative score
    Negative_Score = negative_sc(clean_test)
    # print('Negative_Score = ',Negative_Score)

    # Polarity Score
    Polarity_Score = (Positive_Score - Negative_Score) / ((Positive_Score + Negative_Score) + 0.000001)
    # print('Polarity_Score = ',Polarity_Score)

    # Subjectivity Score
    Subjectivity_Score = (Positive_Score - Negative_Score) / ((len(clean_test)) + 0.000001)


    # print('Subjectivity_Score = ',Subjectivity_Score)

    # Function to count syllables
    def syllable_count(word):
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        # removing exceptional case
        if word.endswith("e" or 'es' or 'ed'):
            count -= 1
        if count == 0:
            count += 1
        return count


    # print(syllable_count('Burger'))

    # Counting sum of total no.of syllables
    def syllable_count_per_word(w):
        n = 0
        for i in w:
            n = n + syllable_count(i)

        return n


    # Counting no.of syllables>2
    def complex_words_count(w):
        n = 0
        for i in w:
            if syllable_count(i) > 2:
                n += 1
        return n


    # Complex Word Count
    Complex_Word_Count = complex_words_count(clean_test)
    # print('Complex_word_count = ',Complex_Word_Count)

    # Average Sentence Length
    Average_Sentence_Length = total_number_of_words / len(sentence_data)
    # print('Average_Sentence_Length = ',Average_Sentence_Length)

    # Percentage of Complex words
    Percentage_of_Complex_words = Complex_Word_Count / len(clean_test)
    # print('Percentage_of_Complex_words =',Percentage_of_Complex_words)

    # Fog Index
    Fog_Index = 0.4 * (Average_Sentence_Length + Percentage_of_Complex_words)
    # print('Fog_Index = ',Fog_Index)

    # Average Number of Words Per Sentence
    Average_Number_of_Words_Per_Sentence = len(clean_test) / len(sentence_data)
    # print('Average_Number_of_Words_Per_Sentence = ',Average_Number_of_Words_Per_Sentence)

    # Word Count
    Word_count = len(clean_test)
    # print('Word_count = ',Word_count)

    # Syllable per word
    Syllable_per_word = syllable_count_per_word(clean_test)
    # print('Syllable_per_word',Syllable_per_word)

    # Personal pronouns
    pronoun_re = re.compile(r'\b(I|we|my|ours|(?-i:us))\b', re.I)
    pp = pronoun_re.findall(data)
    Personal_pronouns = len(pp)
    # print('Personal_pronouns = ',Personal_pronouns)

    # Average word length
    Average_word_length = (sum(len(i) for i in clean_test)) / len(clean_test)
    # print('Average_word_length = ',Average_word_length)

    output_values = [Positive_Score, Negative_Score, Polarity_Score, Subjectivity_Score, Average_Sentence_Length,Percentage_of_Complex_words,
                       Fog_Index,
                     Average_Number_of_Words_Per_Sentence, Complex_Word_Count, Word_count, Syllable_per_word, Personal_pronouns, Average_word_length]
    lmkt.append(output_values)
    #print(f'{i}_id = ',output_values)

#print(lmkt)
indices = list(range(37,151))


cols = ['POSITIVE SCORE','NEGATIVE SCORE','POLARITY SCORE','SUBJECTIVITY SCORE','AVG SENTENCE LENGTH','PERCENTAGE OF COMPLEX WORDS','FOG INDEX',
         'AVG NUMBER OF WORDS PER SENTENCE','COMPLEX WORD COUNT','WORD COUNT','SYLLABLE PER WORD','PERSONAL PRONOUNS','AVG WORD LENGTH']

df2 =pd.DataFrame(lmkt,index=indices,columns=cols)

df = pd.read_excel("Input.xlsx")
df = df[['URL_ID','URL']]
df2 = df2.reset_index()
#print(df2)

#merging df & df2 into dfs1
dfs1=df.merge(df2,left_on='URL_ID',right_on='index',how='inner').drop('index',axis = 1)

#Exporting data into excel
dfs1.to_excel('Output_Analysis.xlsx',index= False)

