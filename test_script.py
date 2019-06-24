#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 21:46:38 2019

@author: danielludewig
"""

home = test.loc[test.Round.str.startswith("Round"),
                ["HomeTeam","HomePts","AwayPts"]]
away = test.loc[test.Round.str.startswith("Round"),
                ["AwayTeam","AwayPts","HomePts"]]

cols = ["Team", "Pts", "OpPts"]

home.columns = cols
away.columns = cols

comb = pd.concat([home, away], sort = True)

comb.Team = comb.Team.str.strip()

comb["Win"] = comb.apply(lambda x: 1 if x.Pts > x.OpPts else 0, axis =1)
comb["Draw"] = comb.apply(lambda x: 1 if x.Pts == x.OpPts else 0, axis =1)
comb["Loss"] = comb.apply(lambda x: 1 if x.Pts < x.OpPts else 0, axis =1)


teamSum = pd.concat([comb.Team.value_counts(), 
                     comb.groupby("Team").sum()], axis = 1, sort = True)

teamSum["CompPnts"] = teamSum.Win * 4 + teamSum.Draw * 2


# test comtested posessions
teststats.Team = teststats.Team.str.strip()
cp = teststats.groupby("Team")[["CP"]].sum()

teamSum = pd.merge(teamSum, cp, left_index = True, right_index = True)

import matplotlib.pyplot as plt
import seaborn as sns

sns.regplot("CompPnts", "CP", data = teamSum)

import numpy as np
np.corrcoef(teamSum.CompPnts, teamSum.CP)[0][1]**2




