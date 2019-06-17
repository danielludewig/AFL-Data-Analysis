#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 21:46:38 2019

@author: danielludewig
"""

statsurl = "https://afltables.com/afl/stats/games/2018/122020180324.html"


html  = urlopen(statsurl).read()

soup  = bs(html, "html.parser")

stats = pd.read_html(soup.prettify())

first = stats[0]
secon = stats[1]
third = stats[2]
forth = stats[3]
fifth = stats[4]
sixth = stats[5]
seven = stats[6]
kates = stats[7]
nines = stats[8]



rnd = [x for x in first.loc[0,1].split(" ") if x != ""][1]

team_one = third.columns.levels[0][0].split(" ")[0]

team_two = fifth.columns.levels[0][0].split(" ")[0]

third.columns = [third.columns.levels[1][x] for x in third.columns.labels[1]]

coltokeep = [x for x in third.columns if "Unnamed" not in x]

teamOneStats = third.loc[third.loc[:,"#"] != "Rushed",coltokeep].fillna(0)
teamOneStats["Team"] = team_one   
                                   

fifth.columns = [fifth.columns.levels[1][x] for x in fifth.columns.labels[1]]
                                   
teamTwoStats = fifth.loc[fifth.loc[:,"#"] != "Rushed",coltokeep].fillna(0)
teamTwoStats["Team"] = team_two 
                  
                                   
comb = pd.concat([teamOneStats, teamTwoStats], 
                 axis = 0, sort = True).reset_index(drop = True)

comb["Round"] = rnd

for col in comb.columns:
    if col not in ("Team", "Player", "Round"):
        comb[col] = comb[col].astype(int)


for df in stats:
    if isinstance(df.columns, pd.core.indexes.multi.MultiIndex):
        print(df.shape)
        header =  df.columns.levels[0][df.columns.labels[0][0]]
        if "Match" in header:
            header = header.replace("Match", "---")
            team = header.split("---")[0]
            print(team)





