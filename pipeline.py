# -*- coding: utf-8 -*-
"""pipeline.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zh8y85RkEsqi7x6qea0NIIrLU57Nnk2e
"""

# Parsing the parameters
import configparser
import os
import warnings
warnings.filterwarnings("ignore")

# Text Processing Libraries
import re
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
#nltk.download('all', quiet=True)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Library for model binary file
import pickle

# LIbraries for general data processing
import pandas as pd
import numpy as np

# Libraries for feature engineering.
from sklearn.feature_extraction.text import CountVectorizer

# classification libraries
from skmultilearn.problem_transform import BinaryRelevance
from sklearn.linear_model import LogisticRegression


########################### READ PARAMETERS ##########################
# READ THE PARAMETERS
root_path = os.getcwd()
ini_path = os.path.join(root_path,'config.ini')
ini_path = ini_path.replace('\\', '/')
parser = configparser.ConfigParser()
parser.read(ini_path)

# paramters from config.ini
vectorizer_name = parser.get('parameters', 'vectorizer_name')
model_name = parser.get('parameters', 'model_name')
model_path = root_path

labels = parser.get('parameters', 'labels')
labels = labels[1:-1]
labels = labels.split(',')
labels = [x.replace("'", '').strip() for x in labels]

common_words = parser.get('parameters', 'common_words')
common_words = common_words[1:-1]
common_words = common_words.split(',')
common_words = [x.replace("'", '').strip() for x in common_words]

######################################################################
#################### MODULE 1 - TEXT CLEANING ########################
######################################################################
def data_cleaning(text):
    
    '''
    Steps
    1. lower text
    2. remove unicode
    3. remove stop words
    4. remove numbers
    5. remove trailing spaces
    6. Lemmitization.
    7. Remove common words
    
    Args
    
    Input  - string (abuse text)
    Output - string (cleaned abuse text)
    '''
    
    # 1. Lower the text
    text = text.lower()

    # 2. Removing Unicode Characters
    pattern = r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?"
    text = re.sub(pattern, "", text)

    # 3. Removing Stopwords
    stop = stopwords.words('english')
    text = " ".join([word for word in text.split() if word not in (stop)])

    # 4. Remove numbers
    text = re.sub(r'\d+', '', text)

    # 5. Remove trailing spaces
    text = re.sub('\s+', ' ', text).strip()

    # 6. Lemmatization
    lemmatizer = WordNetLemmatizer()
    text = ' '.join([lemmatizer.lemmatize(word) for word in text.split(' ')])

    # 3. Removing common words
    text = " ".join([word for word in text.split() if word not in (common_words)])
  
    return text

######################################################################
#################### MODULE 2 - Load Count Vectorizer ################
######################################################################
def load_vectorizer(path):
    '''
    Module takes path as input and loads
    the count vectorizer model from the 
    pickle file.
    
    Args
    
    Input - String (location of the vectorizer model)
    Output - Model (vectorizer - unigram based count vectorizer)
    '''
  
    # load feature vectorizer
    vec_pickle_in = open(path, 'rb')
    vectorizer = pickle.load(vec_pickle_in)

    return vectorizer

######################################################################
#################### MODULE 3 - Exract Features ######################
######################################################################

def feature_generation(text, vectorizer):
    
    '''
    Module takes text and count vectorizer model as input
    and extracts features as numpy as array.
    
    Args:
    
    Input
    -----
    1. text - String (abuse text)
    2. vectoirzer - count vectorizer model
    
    Output
    ------
    1. bow_unigram - numpy array (features are numpy array)
    
    '''

    # create dataframe of text
    df = pd.DataFrame({'clean_desc_lemma': [text]})

    # COUNT VECTORIZER - UNI GRAM
    X = vectorizer.transform(df['clean_desc_lemma'])

    bow_unigram_df = pd.DataFrame(X.toarray(),columns=vectorizer.get_feature_names())

    # convert data frame to numpy array
    bow_unigram = bow_unigram_df.to_numpy()

    return bow_unigram


######################################################################
#################### MODULE 4 - Load Model ###########################
######################################################################
def load_model(path):
    
    '''
    Module takes path as input and loads
    the classification model from the 
    pickle file.
    
    Args
    
    Input - String (location of the  model)
    Output - Model (classifier - logistic regression based model)
    '''

    # load ml model
    model_pickle_in = open(path, 'rb')
    model = pickle.load(model_pickle_in)

    return model

######################################################################
#################### MODULE 4 - Prediction ###########################
######################################################################
def predict(clf, text):
    
    '''
    Module takes vectorised text and classifier as input 
    and predicts the abuse type.
    
    Args
    
    Input - numpy array (vectorized text)
          - model (classifier - logistic regression based model)
          
    Output - numpy array
    '''

    # prediction
    text_pred = clf.predict(text)

    # convert sparse matrix to dense numpy array
    text_pred = np.asarray(text_pred.todense())

    # faltten the array
    text_pred = text_pred.flatten()

    return text_pred


######################################################################
#################### MODULE 5 - Predicted Lable ######################
######################################################################
def get_label(label, text_pred):
    
    '''
    Module takes numpy array of labels and prediction as input.
    returns list of multi label abuse types.
    
    Args
    
    Input - label (list)
          - text prediction (numpy array of prediction)
          
    Output - abuse type (list of abuse type)
    '''
    
    # initiate result
    text_pred= list(text_pred)
    result = []
    for i in range(len(label)):
        if (text_pred[i]) == 1:
            result.append(label[i])
            
    if text_pred == [0,0,0]:
        result.append('Other Abuse Type')
        
    return result

######################################################################
#################### MODULE 6 - Prediction Pipeline ##################
######################################################################
def predict_abuse_type(text):

    '''
    Modeul runs the below steps.
    1. Data Cleaning
    2. Feature engineering
    3. Model
    4. Predict
    '''
    # original text
    text_original = text

    # data cleaning
    text = data_cleaning(text)

    #################### feature engineering ##################

    ### vectorizer path
    path = f'{model_path}/{vectorizer_name}'

    ### load vectorizer
    vectorizer = load_vectorizer(path)

    ### features
    text = feature_generation(text, vectorizer)

    ###################### Model ###############################

    ### model path
    path = f'{model_path}/{model_name}'
    clf = load_model(path)

    ### prediction
    text_pred = predict(clf, text)

    ### result
    result = get_label(labels,  text_pred)

    # print results
    print(f'Abuse user input : \033[1m {text_original} \033[0m \n\nAbuse type of user input \033[1m {result} \033[0m')

    return result
