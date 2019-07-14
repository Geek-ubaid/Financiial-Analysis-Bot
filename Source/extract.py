# coding: utf-8
from __future__ import print_function

import tabula
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pytesseract
import cv2 as cv
import requests

def format_data(data):
    bool_val = data.apply(lambda row: row.astype(str).str.lower().str.contains('equity and liabilities').any(), axis=1)
    if (bool_val == True).any() :
        get_main_headers(data)
    
def get_main_headers(data):
    for i in range(len(data)):
        print(np.isin(data.iloc[i,1:].values,['NaN']).all())
        if np.isin(data.iloc[i,1:],[np.nan]).all():
            print(data.iloc[i,1:])
            
def reshape_data(data):
    pass

def extract_image_data(file):
    payload = {'isOverlayRequired': False,
               'apikey': 'cb7978d6cf88957',
               'language': 'eng',
               'isTable': 'true',
               'detectOrientation': 'true'
               }
    with open(file, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={file: f},
                          data=payload,
                          )
    return r.content.decode()

def extract_data_using_ocr(file,pages):
    payload = {'isOverlayRequired': False,
               'apikey': 'cb7978d6cf88957',
               'language': 'eng',
               'isTable': 'true',
               'detectOrientation': 'true'
               }
        
    with open(file, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={file: f},
                          data=payload,
                          )
    return r.content.decode()

def extract_pdf_data(file,page_no):
    try:
        data = tabula.read_pdf(file,pages=int(page_no))
        formt_data = rebuild_data(data)
        return formt_data
    except:
        return []

def highlight_bold(s):
    print(s['Equity and liabilities'])
    return ['background-color: yellow' if v == 0 else '' for v in s]

def rebuild_data(data):
    data_df = data.drop(data.columns[[1, 3, 5]], axis=1)
    data_df.columns = data_df.iloc[0]
    data_df = data_df.dropna(how='all')
    data_df = data_df.iloc[1:]

    data_df['Equity and liabilities'] = data_df.apply(get_group_type,axis=1)
    data_df.style.highlight_null(null_color='red')
    print(data_df.head())
    del(data_df['Equity and liabilities'])
    return data_df

def get_group_type(row):
    if type(row[1]) == np.float and type(row[2]) == np.float:
         return 0
    else:
        return 1

def processed_ocr_result(df):
    try:
        import yaml
        import pprint
        import ast
        processed_df = yaml.load(df)
        for i in processed_df['ParsedResults'][0]['ParsedText'].split('\r\n'):
            print(i)
    except:
        raise TypeError

def extract_file(file_name,pages):
    
    if file_name.endswith('.pdf'):
        df = extract_pdf_data(file_name,pages)
        if len(df) == 0:
            df = extract_data_using_ocr(file_name,pages)
            processed_ocr_result(df)
        else:
            df.to_excel('text.xlsx','Balancesheet')
            return True

    elif file_name.endswith('.jpg'):
        df = extract_image_data(file_name)
        processed_ocr_result(df)
        return True

    else:
        return False

if __name__ == "__main__":
    file_name = input('enter file name:')
    pages = input('Enter Balance sheet page no:')
    comapny_name = input('Enter company name:')
    extract_file(file_name,pages)




