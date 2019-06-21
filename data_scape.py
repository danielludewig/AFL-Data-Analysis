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
from itertools import chain
from datetime import datetime

# Write function to scrape a single season of AFL data
def getAFLResults(year):
    # Get time function starts to run
    startTime = datetime.now()
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
    
    # Lets look at the links to the game stats
    atabs    = soup.find_all("a")
    allLinks = [re.findall('href="(.*html)"', str(a)) for a in atabs] 
    relLinks = [link for link in list(chain(*allLinks)) if "games" in link]
    
    noOfLinks = len(relLinks)
    
    # Loop through the links, and scrape the stats for each match 
    allStats = pd.DataFrame()
    
    for l_no, link in enumerate(relLinks):
        
        st = "https://www.afltables.com/afl"
        
        link = st + link.replace("..","").replace("\n", "")
        
        try:
            html  = urlopen(link).read()
            soup  = bs(html, "html.parser")
            stats = pd.read_html(soup.prettify())

        except:
            print("Error with link: " + link)
                      
        comb = pd.DataFrame()
  
          
        for df in stats:
                
            if isinstance(df.columns, pd.core.index.Int64Index):
                if "Round" in str(df.loc[0,1]):
                    val = df.loc[0,1]
                    rnd = [x for x in val.split(" ") if x!= ""][1]
                
            elif isinstance(df.columns, pd.core.indexes.multi.MultiIndex):
                header =  df.columns.levels[0][df.columns.labels[0][0]]
                if "Match" in header:
                    header = header.replace("Match", "---")
                    team = header.split("---")[0]
                    
                    lvls = df.columns.levels[1]
                    labs = df.columns.labels[1]
                    
                    cols = [lvls[x] for x in labs]
                    df.columns = cols
                    
                    colsKp = [x for x in df.columns if "Unname" not in x]
                    
                    output = df.loc[~df.loc[:,"#"].isin(["Rushed", "Totals"]),
                                    colsKp]
                    output = output.fillna(0)
                    output["Team"] = team
                    
                    comb = pd.concat([comb, output], axis = 0, 
                                     sort = True).reset_index(drop = True)

            comb["Round"] = rnd
            
            allStats = pd.concat([allStats, comb], sort = True)
            
            if l_no+1 % 20 == 0:
                print(str(l_no+1) + " links complete. " + 
                      str(round((l_no+1)*100/noOfLinks, 1)) + "% Complete.")
            
        for col in allStats.columns:
            if col not in ("Team", "Player", "Round"):
                allStats[col] = allStats[col].astype(int)
    
    print("Data scrape complete. Script time:")
    print(datetime.now() - startTime)
        
    return totalDF.reset_index(drop = True), totalTable, allStats



## Test case, as example
    
# =============================================================================
# year = 2018
# test, testtable, teststats = getAFLResults(2018)
# =============================================================================








