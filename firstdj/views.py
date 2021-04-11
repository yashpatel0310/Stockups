# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django import template
import yfinance as yf
from .utils import get_plot
import matplotlib.pyplot as plt
import json 
from .form import stocklist
import math
import keras
import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from keras.optimizers import SGD




def index(request):
    ticker = 'AAPL'
    senx=yf.download(tickers='^BSESN', period='100d')
    senx_close = senx['Close'].to_numpy()
    sensex = senx_close.tolist()

    nift=yf.download(tickers='^NSEI', period='100d')
    nift_close = nift['Close'].to_numpy()
    nifty = nift_close.tolist()
    
    label1 =[]
    for i in range (1,100):
        label1.append(i)
    label2 =[]
    for i in range (1,131):
        label2.append(i)
    stdata = []
    form = stocklist(request.POST)
    if form.is_valid():
        ticker= form.cleaned_data.get("stock_tick")
    tic = ticker

    df=yf.download(tickers=tic, period='1256d')

    maindf = df.reset_index()['Close']

    sc = MinMaxScaler(feature_range = (0, 1))
    maindf = sc.fit_transform(np.array(maindf).reshape(-1,1))

    training_size=int(len(maindf)*0.65)
    test_size=len(maindf)-training_size
    train_data,test_data=maindf[0:training_size,:],maindf[training_size:len(maindf),:]

    def create_dataset(dataset, time_step=1):
        dataX, dataY = [], []
        for i in range(len(dataset)-time_step-1):
            a = dataset[i:(i+time_step), 0]   
            dataX.append(a)
            dataY.append(dataset[i + time_step, 0])
        return np.array(dataX), np.array(dataY)

    time_step = 100
    X_train, y_train = create_dataset(train_data, time_step)
    X_test, ytest = create_dataset(test_data, time_step)

    X_train =X_train.reshape(X_train.shape[0],X_train.shape[1] , 1)
    X_test = X_test.reshape(X_test.shape[0],X_test.shape[1] , 1)

    opt = SGD(lr=0.001)
    model=Sequential()
    model.add(LSTM(256,return_sequences=True,input_shape=(100,1)))
    model.add(LSTM(128,return_sequences=True))
    model.add(LSTM(64))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error',optimizer='adam')
    model.fit(X_train,y_train,validation_data=(X_test,ytest),epochs=100,batch_size=64,verbose=1)



    train_predict=model.predict(X_train)
    test_predict=model.predict(X_test)
    train_predict=sc.inverse_transform(train_predict)
    test_predict=sc.inverse_transform(test_predict)

    trainScore=math.sqrt(mean_squared_error(y_train,train_predict))
    print('Train Score: %.2f RMSE' % (trainScore))
    testScore = math.sqrt(mean_squared_error(ytest,test_predict))
    print('Test Score: %.2f RMSE' % (testScore))



    x_input=test_data[40:].reshape(1,-1)
    temp_input=list(x_input)
    temp_input=temp_input[0].tolist()

    lst_output=[]
    n_steps=400
    i=0
    while(i<=30):
    
        if(len(temp_input)>400):
            x_input=np.array(temp_input[1:])
        
            x_input=x_input.reshape(1,-1)
            x_input = x_input.reshape((1, n_steps, 1))
            yhat = model.predict(x_input, verbose=0)
        
            temp_input.extend(yhat[0].tolist())
            temp_input=temp_input[1:]
            lst_output.extend(yhat.tolist())
            i=i+1
        
        else:
        
            x_input = x_input.reshape((1, n_steps,1))
            yhat = model.predict(x_input, verbose=0)
        
            temp_input.extend(yhat[0].tolist())
        
            lst_output.extend(yhat.tolist())
            i=i+1
    
    
    zeros = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        
    
    stdata = sc.inverse_transform(maindf[1156:]).tolist()
    preditdata = sc.inverse_transform(lst_output).tolist()
    prediction = [*zeros, *preditdata]

    return render(request, 'dashboard.html', { 'label1': label1,'label2': label2,'sensex': sensex,'nifty': nifty,'form':form,'stdata':stdata,'prediction':prediction})

  
def get_data(request):
   
    senx=yf.download(tickers='^BSESN', period='100d')
    senx_close = senx['Close'].to_numpy()
    sensex = senx_close.tolist()

    nift=yf.download(tickers='^NSEI', period='100d')
    nift_close = nift['Close'].to_numpy()
    nifty = nift_close.tolist()
    
    labels =[]
    for i in range (1,100):
        labels.append(i)
    
    return render(request, 'dashboard.html', { 'labels': labels,'sensex': sensex,'nifty': nifty,})

