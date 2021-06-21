# -*- coding: utf-8 -*-
"""Group 1 MPR (COVID 19 predictor).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17SaNoJxsKGAJk3_BLRhjXlOHjd7LdXej
"""

import pmdarima as pm
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.model_selection import TimeSeriesSplit
import pandas as pd
import numpy as np
import datetime
import requests
import warnings
 
import matplotlib.pyplot as plt
import matplotlib

from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from statsmodels.tsa.statespace.sarimax import SARIMAX

import streamlit as st

warnings.filterwarnings('ignore')
st.set_option('deprecation.showPyplotGlobalUse', False)

path = "C:/Users/91908/Downloads/districts.csv"
df = pd.read_csv(path)

st.title("COVID 19 Case Predictor")

district_list = df.District
district_list = district_list.to_list()
    
dist_list = []
    
for dist in district_list:
    if dist not in dist_list:
        dist_list.append(dist)
    
nav = st.sidebar.radio("Navigation", ["Home", "Projection","Projection Accuracy", "Datasets", "About us"])
#st.write(df)

#df.head()
try:
    
    if nav == "Home":
        st.header("Home")
        st.write('''Coronavirus disease 2019 (COVID-19) is a contagious respiratory and vascular disease caused by severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2). COVID 19 originating from Wuhan has spread worldwide causing a global pandemic.
    We are introducing a system that forecasts the number of cases arising in the future in every district in India.''')
    
        dist = st.text_input("Enter your district")
    
        flag = False

        for d in dist_list:
            if d.lower() == dist.lower():
                flag = True
                dist = d
                break
            else:
                flag = False
        
        if flag == False:
            st.write("Please enter a valid district name")
    
        df = df[df['District'] == dist]
    
        d = df.loc[:,['Date', 'Confirmed']]
        d = d.sum(axis=1)
        d = d.to_list()
    
        dataset = pd.DataFrame(columns=['ds', 'y'])
        dates = list(df.Date)
        dates = list(pd.to_datetime(dates))
        dataset['ds'] = dates
        dataset['y'] = d
        dataset=dataset.set_index('ds')
        dataset = dataset.loc['2020-04-29':'2020-12-15']
    
        st.subheader("Cumulative Daily Confirmed Cases")
        st.write("This is a graph of number of Cumulative Daily Confirmed Cases in ",dist,"district.")
        plt.figure(figsize=(10, 10))
        plt.plot(dataset, label = 'Cumulative Daily Confirmed Cases')
        plt.xlabel('Days')
        plt.ylabel('Confirmed Cases')
        plt.legend()
        #plt.savefig('Cummulative daily confirmed cases', bbox_inches='tight', transparent=False)
        st.pyplot()
    
        st.subheader("Daily Confirmed Cases")
        st.write("This is a graph of number of Daily Confirmed Cases in ",dist,"district.")
        plt.figure(figsize=(10, 10))
        plt.plot(dataset.diff(), label = 'Daily Cases')
        plt.xlabel('Days')
        plt.ylabel('Confirmed Cases')
        plt.legend()
        #plt.savefig('Daily Cases', bbox_inches='tight', transparent=False)
        st.pyplot()
    
    if nav == "Projection":
        st.header("Projection")
        dist = st.text_input("Enter your district")
    
        flag = False

        for d in dist_list:
            if d.lower() == dist.lower():
                flag = True
                dist = d
                break
            else:
                flag = False
        
        if flag == False:
            st.write("Please enter a valid district name")
        
        st.write("The following graph shows the recorded data until today in blue. Our predictions for the upcoming days follows in orange colour.")
    
        df = df[df['District'] == dist]
    
        d = df.loc[:,['Date', 'Confirmed']]
        d = d.sum(axis=1)
        d = d.to_list()
    
        dataset = pd.DataFrame(columns=['ds', 'y'])
        dates = list(df.Date)
        dates = list(pd.to_datetime(dates))
        dataset['ds'] = dates
        dataset['y'] = d
        dataset=dataset.set_index('ds')
        
        dataset = dataset.diff()
        dataset = dataset.loc['2020-04-29':'2020-12-15']
        
        start_date = '2020-12-15'
        
        train = dataset.loc[dataset.index < pd.to_datetime(start_date)]
        test = dataset.loc[dataset.index >= pd.to_datetime(start_date)]
        
        model = pm.auto_arima(train, start_p=1, start_q=1,
                              test='adf',       # use adftest to find optimal 'd'
                              max_p=3, max_q=3,  # maximum p and q
                              m=1,              # frequency of series
                              d=None,           # let model determine 'd'
                              seasonal=False,   # No Seasonality
                              start_P=0,
                              D=0,
                              trace=True,
                              error_action='ignore',
                              suppress_warnings=True,
                              stepwise=True)
        
        #print(model.summary())
        
        model = SARIMAX(train, order=(3,1,3))
        results = model.fit(disp=True)
        
        sarimax_prediction = results.predict(start=start_date, end='2020-12-31', dynamic=False)
        plt.figure(figsize=(10, 5))
        l1, = plt.plot(dataset, label='Real Time Data')
        l2, = plt.plot(sarimax_prediction, label='Predictions')
        plt.legend(handles=[l1, l2])
        #plt.savefig('SARIMAX prediction', bbox_inches='tight', transparent=False)
        st.pyplot()
        
    
    if nav == "Projection Accuracy":
        st.header("Projection Accuracy")
        dist = st.text_input("Enter your district")
        
        flag = False

        for d in dist_list:
            if d.lower() == dist.lower():
                flag = True
                dist = d
                break
            else:
                flag = False
        
        if flag == False:
            st.write("Please enter a valid district name")
            
        st.write("This is a graph of Real time data vs the Predictions that our mdoel made for the last month")
        st.write("The blue line represents Real time data whereas the orange line shows the projections.")
    
        df = df[df['District'] == dist]
    
        d = df.loc[:,['Date', 'Confirmed']]
        d = d.sum(axis=1)
        d = d.to_list()
    
        dataset = pd.DataFrame(columns=['ds', 'y'])
        dates = list(df.Date)
        dates = list(pd.to_datetime(dates))
        dataset['ds'] = dates
        dataset['y'] = d
        dataset=dataset.set_index('ds')
        
        dataset = dataset.diff()
        dataset = dataset.loc['2020-04-29':'2020-11-30']
        
        start_date = '2020-11-01'
        
        train = dataset.loc[dataset.index < pd.to_datetime(start_date)]
        test = dataset.loc[dataset.index >= pd.to_datetime(start_date)]
        
        model = pm.auto_arima(train, start_p=1, start_q=1,
                              test='adf',       # use adftest to find optimal 'd'
                              max_p=3, max_q=3,  # maximum p and q
                              m=1,              # frequency of series
                              d=None,           # let model determine 'd'
                              seasonal=False,   # No Seasonality
                              start_P=0,
                              D=0,
                              trace=True,
                              error_action='ignore',
                              suppress_warnings=True,
                              stepwise=True)
        
        #print(model.summary())
        
        model = SARIMAX(train, order=(3,1,3))
        
        results = model.fit(disp=True)
        
        month_data = dataset.loc['2020-04-29':'2020-11-30']
        
        sarimax_prediction = results.predict(start=start_date, end='2020-11-30', dynamic=False)
        plt.figure(figsize=(10, 5))
        mae = mean_absolute_error(sarimax_prediction, test)
        l1, = plt.plot(month_data, label='Real Time Data')
        l2, = plt.plot(sarimax_prediction, label='Predictions')
        plt.legend(handles=[l1, l2])
        #plt.savefig('SARIMAX prediction', bbox_inches='tight', transparent=False)
        st.pyplot()
        
        st.write("To check the error margins for future projections, select the checkbox below.")
        check = st.checkbox("Show Real time vs Predictions Fluctuations")
        if check == True:
            st.write("This is the average difference between real time data and predictions each day.")
            st.write("Difference Margin: ", round(mae))
    
    if nav == "Datasets":
        st.header("Datasets")
        st.write("The dataset used in this project was retrieved from covid19india.org")
        st.write("It uses state bulletins and official handles to update the dataset regularly.")
        st.write("To have a look at the dataset, select the checkbox below.")
        check = st.checkbox("Show dataset")
        if check == True:
            st.write(df)
        
    if nav == "About us":
        st.header("About Us")
        st.write("This project is an initiative towards getting accurate predictions about the number of COVID-19 cases arisisng on a local basis.")
        st.write("The idea is to create awareness in the people about the upcoming situations in their locality.")
        st.subheader("Project Created by")
        st.write("Shashank Karna")
        st.subheader("Suggestions")
        suggestion = st.text_area("Please feel free to drop some suggestions")
        st.subheader("Queries")
        st.write("For any queries contact us via the following details")
        st.write("Email ID: shashankkarna.32.g.fe@gmail.com")
        
        st.subheader("THANK YOU!!!")
except:
    pass