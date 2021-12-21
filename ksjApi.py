#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import requests
import pgOperation
import math
import dateOperation as dp
import datetime
import random
import hmac
import hashlib
import base64

def sha256(jsonBody,appSecret):
    sha256HMAC = hmac.new(bytes(appSecret , 'utf-8'), msg = bytes(jsonBody , 'utf-8'), digestmod = hashlib.sha256).hexdigest().upper()
    sha256HMAC_bytes = bytearray.fromhex(sha256HMAC)
    signature = base64.urlsafe_b64encode(sha256HMAC_bytes)
    if signature[-1] == '=':
        signature = signature[:-1]
    return signature


class APIUtils:

    # 构造函数
    def __init__(self, aesParams, appSecret,appId,version,method,pageSize):
        self.aesParams = aesParams
        self.appSecret = appSecret
        self.appId = appId
        self.version = version
        self.method = method
        self.pageSize = pageSize


    def getDatabyApi(self, currentPage, pageSize):
        nonce = str(random.randint(0,100000))
        d = datetime.datetime.now()
        timestamp = str(int(datetime.datetime.timestamp(d)*1000))
        jsonBody = "{\"syncInfo\":{\"parameters\":\"" + self.aesParams + "\",\"timestamp\":%s,\"name\":\"主数据\"},\"pageInfo\":{\"currentPage\":%d,\"pageSize\":%d}}"%(timestamp, currentPage, pageSize)
        requestPayload = (sha256(jsonBody,self.appSecret)).decode("utf-8")
        if requestPayload[-1] == '=':
            requestPayload = requestPayload[:-1]
        signdata = "timestamp=" + str(timestamp) + "&method="+self.method+"&version=" + str(self.version) + "&appId=" + self.appId + "&nonce=" + str(nonce) + "&requestPayload=" + str(requestPayload)
        sign = (sha256(signdata,self.appSecret)).decode("utf-8")
        if sign[-1] == '=':
            sign = sign[:-1]
        url =  "https://xxx.xxx/openapi?timestamp=" + timestamp +         "&method="+self.method+"&version=" + self.version + "&" +         "appId=" + self.appId + "&" +         "nonce=" + nonce + "&" +         "requestPayload=" + requestPayload + "&" +         "sign=" + sign
        res = requests.post(url,data=jsonBody.encode('utf-8'), headers={'Content-Type':'application/json'})
        result = res.json()
        res.close()
        return result

    def getIncrementDatabyApi(self, businessDate, currentPage, pageSize):
        nonce = str(random.randint(0,100000))
        d = datetime.datetime.now()
        timestamp = str(int(datetime.datetime.timestamp(d)*1000))
        jsonBody = "{\"syncInfo\":{\"parameters\":\"" + self.aesParams + "\",\"timestamp\":%s,\"name\":\"主数据\",\"businessDate\":%s},\"pageInfo\":{\"currentPage\":%d,\"pageSize\":%d}}"%(timestamp,businessDate,currentPage,pageSize)
        print(jsonBody)
        requestPayload = (sha256(jsonBody,self.appSecret)).decode("utf-8")
        if requestPayload[-1] == '=':
            requestPayload = requestPayload[:-1]
        signdata = "timestamp=" + str(timestamp) + "&method="+self.method+"&version=" + str(self.version) + "&appId=" + self.appId + "&nonce=" + str(nonce) + "&requestPayload=" + str(requestPayload)
        sign = (sha256(signdata,self.appSecret)).decode("utf-8")
        if sign[-1] == '=':
            sign = sign[:-1]
        url =  "https://xxx.xxx/openapi?timestamp=" + timestamp +         "&method="+self.method+"&version=" + self.version + "&" +         "appId=" + self.appId + "&" +         "nonce=" + nonce + "&" +         "requestPayload=" + requestPayload + "&" +         "sign=" + sign
        res = requests.post(url,data=jsonBody.encode('utf-8'), headers={'Content-Type':'application/json'})
        result = res.json()
        res.close()
        return result

    def getDfFromJson(self,json):
        json_columns = json['data']['header']
        json_data = json['data']['records']
        json_df = pd.DataFrame(json_data,columns=json_columns)
        return json_df


    def getFullPageNumber(self):
        '''
        return the pageNumber for initial pageSize
        '''
        result = self.getDatabyApi(1,10)
        return math.ceil(result['data']['pageInfo']['totalCount'] / self.pageSize)

    def getIncrementPageNumber(self,businessDate):
        '''
        return the pageNumber for initial pageSize
        '''
        result = self.getIncrementDatabyApi(businessDate, 1, 10)
        return math.ceil(result['data']['pageInfo']['totalCount'] / self.pageSize)

    def getFullDfbyApi(self):
        pages = self.getPageNumber()
        print("total pages is %d"%(pages))
        for page in range(1,pages+1):
            print("now is page %d"%(page))
            data = self.getDatabyApi(page, self.pageSize)
            if page == 1:
                output_df = self.getDfFromJson(data)
            else:
                output_df = pd.concat([output_df,self.getDfFromJson(data)])
        return output_df

    def getIncrementDfbyApi(self, businessDate):
        pages = self.getIncrementPageNumber(businessDate)
        print("total pages is %d"%(pages))
        for page in range(1,pages+1):
            print("now is page %d"%(page))
            data = self.getIncrementDatabyApi(businessDate, page, self.pageSize)
            if page == 1:
                output_df = self.getDfFromJson(data)
            else:
                output_df = pd.concat([output_df,self.getDfFromJson(data)])
        return output_df

    def writeTableByReportSecret(self,pg,table_name):
        '''
        Only for initial process. For increment purpose plz use func named appendIncrementByReportSecret()
        '''
        print("prepare data...")
        df = self.getFullDfbyApi()
        print("write table...")
        pg.writeDfToPg(df,table_name)

    def appendIncrementByReportSecret(self,pg,table_name,businessDate):
        '''
        1. delete data in last 3 days
        2. append data to targeted table
        '''
        print("prepare data...")
        df = self.getIncrementDfbyApi(businessDate)
        print("insert table...")
        condition = "period_key in ('%s', '%s', '%s')"%(dp.date(businessDate,0,-2,0), dp.date(businessDate,0,-1,0), businessDate)
        pg.deleteRowsbyCondition(table_name,condition)
        pg.appendPgTable(df,table_name)
