# -*- coding: utf-8 -*-
from dataloader import loadAll;
import pandas as pd
import os
#import matplotlib as mpl
#mpl.use('TkAgg')
#mpl.use('Qt4agg')
import matplotlib.pyplot as plt
import seaborn; seaborn.set()
############################################################
# Settings
graphsDirName = 'OutPics'
populationRelationScale = 100000
smoothRadius = 1
############################################################
smoothWindow=str(int(smoothRadius)*2 + 1)
columnReplaces = {
    'pop': 'Population',
    'deaths': 'Deaths',
    'recovered': 'Recovered',
    'cases': 'Total cases',
    'area': 'Area',
    'urban': 'Urban percentage',
    'fatality' : 'Death outcome percentage',
    
    'dCases': 'New Cases',
    'dRecovered': 'New Recovered',
    'dDeaths': 'New Deaths',
    
    'deathsPerRec': 'Deaths per Recovered',
    'deathsPerPop': 'Deaths per Population',
    'casesPerPop': 'Cases per Population',
    'dCasesPerPop': 'New Cases per Population',

    'activeCases': 'Active Cases',
    
    'dCasesSmoothed': 'New Cases (' + smoothWindow + '-averaged)',
    'dRecoveredSmoothed': 'New Recovered (' + smoothWindow + '-averaged)',
    'dDeathsSmoothed': 'New Deaths (' + smoothWindow + '-averaged)',

    'deathsPerRecSmoothed': 'Deaths per Recovered (' + smoothWindow + '-averaged)',
    'deathsPerPopSmoothed': 'Deaths per Population (' + smoothWindow + '-averaged)',
    'casesPerPopSmoothed': 'Cases per Population (' + smoothWindow + '-averaged)',
    
    'dCasesPerPopSmoothed': 'New Cases per Population (' + smoothWindow + '-averaged)',

    'activeCasesSmoothed': 'Active Cases (' + smoothWindow + '-averaged)',

    'fatalitySmoothed' : 'Death outcome percentage (' + smoothWindow + '-averaged)'
}
############################################################
def ensureDirsCreated():
    if not os.path.exists(graphsDirName):
        os.makedirs(graphsDirName)
############################################################
def column2Column(c):
    return c if not c in columnReplaces.keys() else columnReplaces[c]
############################################################
def showRating(data, howMany, column, relTo=None, scale=None, doPaint=True, doPrint=False, doSave=False):
    
    if relTo is None or (relTo == 'pop' and scale is None):
        rData = ratingPrimary(data, column, relative=(relTo == 'pop'))
        if scale is None:
            scale = populationRelationScale
    else:
        if scale is None or scale <= 0:
            scale = 1
        rData = ratingRelation(data, column, relTo, scale=scale)

    title = column2Column(column)
    if relTo is not None:
        title = title + ' to ' + ((str(scale) + ' of ') if scale != 1 else '') + column2Column(relTo)
        
    showTop(rData, howMany, title=title, doPaint=doPaint, doPrint=doPrint, doSave=doSave)
############################################################
def showTop(inp, howMany, title='', doPaint=True, doPrint=False, doSave=False):
    data = inp[0].iloc[:howMany] 
    date = date2date(inp[1], addYear=True)
    titleFull = title + " at " + date
    if len(title) < 1:
        title = 'untitled'
    if doPrint:
        print (titleFull)
        print(data)
        
    if not doPaint and not doSave:
        return
    
    yMarks = data['name']
    fig,ax = plt.subplots(1, 1, figsize=(10, howMany/2))
    ax.invert_yaxis()
    ax.barh(yMarks, data['total'], color='#00AA99')
    ax.set_title(titleFull, fontsize=15)
    xoffs = data['total'][1]*0.015
    for i, v in enumerate(data['total']):
        ax.text(v + xoffs, i + .16, str(int(v)), color='black', fontweight='bold')
    lim = ax.get_xlim()
    ax.set_xlim((lim[0], lim[1]*1.08))

    if doSave:
        ensureDirsCreated()
        fig.savefig(graphsDirName + '/' + title + '.png', dpi=100)
        
    #if doPaint:
        #fig.show()
############################################################
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
def date2date(s, addYear=False):
    spl = s.split('/')
    month = months[int(spl[0]) - 1]
    day = int(spl[1])
    year = int('20' + spl[2])
    
    if addYear:
        strRep = '%d %s %d' % (day, month, year)
    else:
        strRep = '%s %d' % (month, day)
        
    return strRep
############################################################
def isDispDate(dStr):
    return dStr.endswith(' 1') or dStr.endswith(' 15')
############################################################
def paintList(data, column, relToCases=False, title=None, doPaint=True, doSave=False):
    fig,ax = plt.subplots(1, 1, figsize=(10, 5))
    #fig,ax = plt.subplots(1, 1)
    ticks = [date2date(s) for s in data[0][1].index.to_list()]
    for country in data:
        ax.plot(country[1]['cases'] if relToCases else ticks, country[1][column], label=country[0])
    ax.legend()
    title = title if title is not None else (column2Column(column) + (' to Total Cases' if relToCases else ''))
    ax.set_title(title, fontsize=15)
    
    fig.canvas.draw()
    
    ax.tick_params(axis='x', rotation=45)
    if not relToCases:
        for label in ax.get_xticklabels():
            if  not isDispDate(label.get_text()):
                label.set_visible(False)
    if doSave:
        ensureDirsCreated()
        fig.savefig(graphsDirName + '/' + title + '.png', dpi=100)
        
    #if doPaint:
        #fig.show()
############################################################
def ratingPrimary(data, column, relative=False):
    dfT = data[0].copy()
    dfT['total'] = dfT[column] if not relative else dfT[column]/dfT['pop']*populationRelationScale
    res = dfT[['name', 'total']].sort_values('total', ascending=False).reset_index(drop=True)[0 if relative else 1:]
    return res, data[1]
############################################################
def ratingRelation(data, nom, denom, scale):
    df = data[0]
    # Throwing away zero-denominated countries. Most probably it's some
    # small uninteresting islands os something like that
    dfT = df[df[denom] != 0].copy()
    
    dfT['total'] = dfT[nom]/dfT[denom]*scale
    res = dfT[['name', 'total']].sort_values('total', ascending=False).reset_index(drop=True)[0:]
    return res, data[1]
############################################################
def mergeForDate(data, date=None):
    cases = data[0]
    deaths = data[1]
    recovered = data[2]

    if date == None:
        date = cases.columns[-1]
        
    casesT = cases[['name', 'pop', 'area', 'urban', date]].copy()
    casesT.rename(columns={date: 'cases'}, inplace=True);
        
    deathsT = deaths[['name', date]].copy()
    deathsT.rename(columns={date: 'deaths'}, inplace=True);
        
    recoveredT = recovered[['name', date]].copy()
    recoveredT.rename(columns={date: 'recovered'}, inplace=True);
    
    res = pd.merge(pd.merge(casesT, deathsT), recoveredT)
    res['fatality'] = res['deaths']*100/(res['recovered'] + res['deaths'])

    return res, date
############################################################
def addSmoothed(df, column, radius):
    radius = int(radius)

    newCol = column + 'Smoothed'

    rows = df.shape[0]
    
    df[newCol] = df[column]
    for pos in range(rows):
        cnt = 1
        for i in range(1, radius + 1):
            if pos >= i:
                df[newCol][pos] += df[column][pos - i]
                cnt += 1
            if pos <= rows - i - 1:
                df[newCol][pos] += df[column][pos + i]
                cnt += 1
        df[newCol][pos] /= cnt
############################################################
def mergeForCountry(data, name='World'):
    cases = data[0]
    deaths = data[1]
    recovered = data[2]
    
    casesT = cases[cases['name'] == name].drop(columns=['name', 'pop', 'area', 'urban'])
    deathsT = deaths[deaths['name'] == name].drop(columns=['name', 'pop', 'area', 'urban'])
    recoveredT = recovered[recovered['name'] == name].drop(columns=['name', 'pop', 'area', 'urban'])
    
    casesT = casesT.transpose()
    casesT.rename(columns={casesT.columns[0]: 'cases'}, inplace=True)
    
    deathsT = deathsT.transpose()
    deathsT.rename(columns={deathsT.columns[0]: 'deaths'}, inplace=True)
    
    recoveredT = recoveredT.transpose()
    recoveredT.rename(columns={recoveredT.columns[0]: 'recovered'}, inplace=True)

    res = pd.merge(pd.merge(casesT, deathsT, left_index=True, right_index=True), recoveredT, left_index=True, right_index=True)
    
    res['pop'] = cases[cases['name']==name]['pop'].iloc[0]
    res['area'] = cases[cases['name']==name]['area'].iloc[0]
    res['urban'] = cases[cases['name']==name]['urban'].iloc[0]
    
    res['deathsPerRec'] = res['deaths']/res['recovered']
    res['deathsPerPop'] = res['deaths']/res['pop']
    res['casesPerPop'] = res['cases']/res['pop']
    res['activeCases'] = res['cases'] - res['deaths'] - res['recovered']
    
    res['dCases'] = res['cases'] - res['cases'].shift(1)
    res['dDeaths'] = res['deaths'] - res['deaths'].shift(1)
    res['dRecovered'] = res['recovered'] - res['recovered'].shift(1)


    addSmoothed(res, 'dCases', smoothRadius)
    addSmoothed(res, 'dDeaths', smoothRadius)
    addSmoothed(res, 'dRecovered', smoothRadius)

    addSmoothed(res, 'deathsPerRec', smoothRadius)
    addSmoothed(res, 'deathsPerPop', smoothRadius)
    addSmoothed(res, 'casesPerPop', smoothRadius)

    addSmoothed(res, 'activeCases', smoothRadius)

    res['dCasesPerPop'] = res['dCases']/res['pop']
    addSmoothed(res, 'dCasesPerPop', smoothRadius)
    
    res['fatality'] = res['deaths']*100/(res['recovered'] + res['deaths'])
    addSmoothed(res, 'fatality', smoothRadius)

    
    return res[1:]
############################################################
def mergeForCountriesList(data, names=['World'], starting_date=None):
    if len(names) < 1:
        return []
    
    return [(n, mergeForCountry(data, n) if starting_date is None else mergeForCountry(data, n).loc[starting_date:]) for n in names]
############################################################
if __name__ == '__main__':
    print('Testing')
    
    data = loadAll(doUpdateGit=True)
    #data = loadAll(doUpdateGit=False)

    today = mergeForDate(data)
    #showRating(today, 10, 'deaths', relTo='area', doSave=True)
    #showRating(today, 10, 'recovered', relTo='pop')
    showRating(today, 20, 'fatality')
    
    
    
    startingDate = None
    #startingDate = '3/1/20'
    countries=['Russia', 'Italy', 'Spain', 'US', 'Germany', 'World']
    #countries=['China']
    data = mergeForCountriesList(data, names=countries, starting_date=startingDate)
    #paintList(data, 'deaths', relToCases=False)
    #paintList(data, 'dDeathsSmoothed', relToCases=False)
    #paintList(data, 'fatalitySmoothed', relToCases=False)
    paintList(data, 'activeCasesSmoothed', relToCases=False)
    #paintList(data, 'deathsPerPopSmoothed', relToCases=True)
    
    #from dataloader import sysExec
    #sysExec('dir', print_stdout=True)
    
    print('Done.')
