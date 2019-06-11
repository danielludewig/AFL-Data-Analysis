#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 18:34:37 2019

@author: danielludewig
"""

# Import packaegs
import pandas as pd
from bs4 import BeautifulSoup as bs
import re
from urllib.request import urlopen

# Write function to scrape a single season of AFL data
def getAFLResults(year):
    # Create html string
    url = "https://afltables.com/afl/seas/" + str(year) + ".html"
    # Read html contents
    html = urlopen(url).read()
    # Create Soup
    soup = bs(html, "html.parser")
    # Parse soup and create list of DFs
    tables = pd.read_html(soup.prettify())
    # Tables of shape (2,2) denote new round
    # Tables of shape (3,4) denote match
    # Tables of shape (20,4) denote ladder
    # Create empty DF for all results
    totalDF = pd.DataFrame()
    totalTable = pd.DataFrame()
    # Loop through list of DFs, create row and add each row to cumlative DF
    ind = 0
    for df in tables:
        ind += 1
        if df.shape == (2,2):
            try:
                rnd = df.loc[0,0]
            except:
                rnd = "Error"
        elif df.shape == (3,4):
            try:
                dt = re.findall("... (.* PM) ", df.loc[0,3])[0]
            except:
                dt = pd.NaT
            att = re.findall("Att: (.*) V", df.loc[0,3])[0].strip()
            ven = re.findall("Venue: (.*)", df.loc[0,3])[0].strip()
            row = pd.Series({"Round"   : rnd,
                             "HomeTeam": df.loc[0,0],
                             "AwayTeam": df.loc[1,0], 
                             "HomePts" : df.loc[0,2], 
                             "AwayPts" : df.loc[1,2], 
                             "HomeSpl" : df.loc[0,1],
                             "AwaySpl" : df.loc[1,1],
                             "Date"    : dt, 
                             "Attend"  : int(att.replace(",", "")), 
                             "Venue"   : ven})
            row.name = str(ind)
            totalDF = totalDF.append(row, sort =  False)
        elif df.shape[1] == 4 and df.shape[0] > 12:
            table = df.dropna().reset_index()
            table.columns = ["Position", 
                             "Team", 
                             "Played", 
                             "Points", 
                             "Points_Percentage"]
            table["Round"] = rnd
            totalTable = totalTable.append(table).reset_index(drop = True)
    
    totalDF.Date = pd.to_datetime(totalDF.Date)
    
    
    return totalDF.reset_index(drop = True), totalTable



## Test case, as example
    
# =============================================================================
# year = 2018
# test, testtable = getAFLResults(2018)
# =============================================================================

