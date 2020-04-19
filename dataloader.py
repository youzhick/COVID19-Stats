# -*- coding: utf-8 -*-
import pandas as pd
import re
import os
import requests as req
import subprocess as sp
############################################################
# Data sources
# https://github.com/CSSEGISandData/COVID-19
populationSourceURL = 'https://www.worldometers.info/world-population/population-by-country/'
############################################################
# Settings
populationFileName = 'Data/population/population.html'
casesFileName = 'Data/cases/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
deathsFileName = 'Data/cases/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
recoveredFileName = 'Data/cases/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
casesGitDirName = 'Data/cases'

# Coming from cases data SCVs:
countryColumnName = 'Country/Region'

nameReps = [
    ('United States', 'US'),
    ('Guam', 'US'),
    ('DR Congo', 'Congo'),
    ('Congo (Kinshasa)', 'Congo'),
    ('Burma', 'Myanmar'),
    ('Korea, South', 'South Korea'),
    ('C&ocirc;te d\'Ivoire', 'Cote d\'Ivoire'),
    ('Taiwan*', 'Taiwan'),
    ('Czech Republic (Czechia)', 'Czechia'),
    ('Hong Kong', 'China'),
    ('Kosovo', 'Serbia'),
    ('MS Zaandam', 'Netherlands'),
    ('Sint Maarten', 'Netherlands'),
    ('Aruba', 'Netherlands'),
    ('Cura&ccedil;ao', 'Netherlands'),
    ('Caribbean Netherlands', 'Netherlands'),
    ('Saint Kitts &amp; Nevis', 'Saint Kitts and Nevis'),
    ('St. Vincent &amp; Grenadines', 'Saint Vincent and the Grenadines'),
    ('Anguilla', 'United Kingdom'),
    ('Gibraltar', 'United Kingdom'),
    ('Gibraltar', 'United Kingdom'),
    ('Cayman Islands', 'United Kingdom'),
    ('Montserrat', 'United Kingdom'),
    ('Isle of Man', 'United Kingdom'),
    ('Saint Helena', 'United Kingdom'),
    ('British Virgin Islands', 'United Kingdom'),
    ('Turks and Caicos', 'United Kingdom'),
    ('Bermuda', 'United Kingdom'),
    ('Cook Islands', 'New Zealand'),
    ('Tokelau', 'New Zealand'),
    ('Niue', 'New Zealand'),
    ('Faeroe Islands', 'Denmark'),
    ('Greenland', 'Denmark'),
    ('French Guiana', 'France'),
    ('Guadeloupe', 'France'),
    ('New Caledonia', 'France'),
    ('French Polynesia', 'France'),
    ('Martinique', 'France'),
    ('Wallis &amp; Futuna', 'France'),
    ('Mayotte', 'France'),
    ('Macao', 'China'),
    ('Marshall Islands', 'US'),
    ('Puerto Rico', 'US'),
    ('R&eacute;union', 'France'),
    ('Saint Martin', 'France'),
    ('Saint Pierre &amp; Miquelon', 'France'),
    ('Saint Barthelemy', 'Netherlands'),
    ('U.S. Virgin Islands', 'US'),
    ('Western Sahara', 'Morocco'),
    ('Sao Tome &amp; Principe', 'Sao Tome and Principe')
]

dropNames = [
    'Yemen', 'North Korea', 'Malawi', 'South Sudan', 'Tajikistan',
    'American Samoa', 'Diamond Princess', 'West Bank and Gaza', 'Comoros',
    'Falkland Islands', 'Channel Islands', 'Kiribati', 'Samoa',
    'Lesotho', 'Micronesia', 'Nauru', 'Northern Mariana Islands', 'Palau',
    'Solomon Islands', 'State of Palestine',
    'Tonga', 'Turkmenistan', 'Tuvalu', 'Vanuatu'
]
############################################################
def sysExec(cmd, print_stdout=False, stripped=True):
    p = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)    
    
    result = []

    while True:
        s = p.stdout.readline()
        if not s:
            s = p.stderr.readline()
        if not s:
            break
        s = s.decode('utf-8', 'ignore') if not stripped else s.decode('utf-8', 'ignore').strip()
        result.append(s)
        if print_stdout:
            print(s, flush=True)
    
    return result
############################################################
def updateGit():
    print ('Updating git repository: ' + casesGitDirName + '...')
    sysExec('git -C ' + casesGitDirName +' checkout master', print_stdout=True)
    sysExec('git -C ' + casesGitDirName +' pull', print_stdout=True)
    print('Repository updated.')
############################################################
def dropByName(df, name):
    ind = df[df['name'] == name].index
    df.drop(ind, inplace=True)
############################################################
def renameCountries(df):
    for name in nameReps:
        df.replace(name[0], name[1], inplace=True)
############################################################
def parsePopLine(str):
    cells = re.findall(r'<td.*?</td', str)
    name = re.findall(r'/">.*?</a', cells[1])[0][3:-3].strip()
    population = int(re.findall(r'>.*?<', cells[2])[0][1:-1].strip().replace(',', ''))
    landAreaKm2 = int(re.findall(r'>.*?<', cells[6])[0][1:-1].strip().replace(',', ''))
    urbanPercent = re.findall(r'>.*?%', cells[10])
    urbanPercent = int(0 if len(urbanPercent) < 1 else urbanPercent[0][1:-1].strip())
    
    return {'name': name, 'pop': population, 'area': landAreaKm2, 'urban': urbanPercent}
# ---------
def loadPopulation():
    if not os.path.exists(populationFileName):
        print('No population file found. Trying to update from WorldMeter...')
        contents = req.get(populationSourceURL)
        if not contents.ok:
            print ('Cannot access WorldMeter.')
            print ('Check your internet connection and try to manually get ', populationSourceURL)
            print ('If succeeded, save it to ', populationFileName)
            return None
        try:
            dirname = os.path.dirname(populationFileName)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            with open(populationFileName, 'w', encoding='utf-8') as f:
                f.write(contents.text)
        except:
            print ('Error saving population data file')
            return None
        
    try:
        popList=[]
        with open(populationFileName, 'r') as f:
            s = f.read()
            # Here's only one table in the file
            for l in re.findall(r'<tr.*?</tr', s)[1:]:
                popList.append(parsePopLine(l))
                
        result = pd.DataFrame(popList)
        renameCountries(result)

        result = result.groupby('name', as_index=False).sum()

        result = result.append(result.sum(numeric_only=True), ignore_index=True)
        result.iloc[-1, 0] = 'World'

    except:
        print ('Error loading population data')
        result = None
        
    return result
############################################################
def loadCases():
    if not os.path.exists(casesFileName) or not os.path.exists(deathsFileName) or not os.path.exists(recoveredFileName):
        print('Cannot find cases data. Have you forgot to update submodules?')
        return None, None, None

    try:
        cases = pd.read_csv(casesFileName).drop(['Lat', 'Long'], axis=1)
        deaths = pd.read_csv(deathsFileName).drop(['Lat', 'Long'], axis=1)
        recovered = pd.read_csv(recoveredFileName).drop(['Lat', 'Long'], axis=1)
        
        renameCountries(cases)
        renameCountries(deaths)
        renameCountries(recovered)
        
        cases = cases.groupby(countryColumnName, as_index=False).sum()
        deaths = deaths.groupby(countryColumnName, as_index=False).sum()
        recovered = recovered.groupby(countryColumnName, as_index=False).sum()
        
        cases.rename(columns={countryColumnName: 'name'}, inplace=True);
        deaths.rename(columns={countryColumnName: 'name'}, inplace=True);
        recovered.rename(columns={countryColumnName: 'name'}, inplace=True);
        
        # They have two Congos with the same data. Remove one
        dropByName(cases, 'Congo (Brazzaville)')
        dropByName(deaths, 'Congo (Brazzaville)')
        dropByName(recovered, 'Congo (Brazzaville)')

        
        cases = cases.append(cases.sum(numeric_only=True), ignore_index=True)
        cases.iloc[-1, 0] = 'World'
        
        deaths = deaths.append(deaths.sum(numeric_only=True), ignore_index=True)
        deaths.iloc[-1, 0] = 'World'
        
        recovered = recovered.append(recovered.sum(numeric_only=True), ignore_index=True)
        recovered.iloc[-1, 0] = 'World'
    except:
        print ('Error loading cases data. ')
        cases = None
        deaths = None
        recovered = None
        
    return cases, deaths, recovered
############################################################
def loadData():
    pop = loadPopulation()
    cases, deaths, recovered = loadCases()
    
    return cases, deaths, recovered, pop
############################################################
def normalize(cases, deaths, recovered, pop):
        
    for name in dropNames:
        dropByName(pop, name)
        dropByName(cases, name)
        dropByName(deaths, name)
        dropByName(recovered, name)
    
    # We'll not make inner join method to identify possible future problens
    cases = pd.merge(pop, cases, how='outer')
    deaths = pd.merge(pop, deaths, how='outer')
    recovered = pd.merge(pop, recovered, how='outer')
    
    failCount = cases[cases.isna().any(axis=1)].shape[0]
    failCount += deaths[deaths.isna().any(axis=1)].shape[0]
    failCount += recovered[recovered.isna().any(axis=1)].shape[0]
    
    if failCount > 0:
        print('WARNING: some countries data is inconsistent. Check names merging.')
    
    #print (pop)
    #print(cases[cases.isna().any(axis=1)])
    #print (res.loc[res['name']=='French Guiana'].iloc[0,:5])
    
    return cases, deaths, recovered
############################################################
def loadAll(doUpdateGit=True):
    if doUpdateGit:
        updateGit()
    
    print('Loading data...')
    cases, deaths, recovered, pop = loadData()
    
    res = normalize(cases, deaths, recovered, pop)
    
    print('Loaded')
    return res
############################################################
if __name__ == '__main__':
    print('Testing')

    a = loadAll()
    cases = a[0]
    print (cases.loc[cases['name']=='United Kingdom'])

    print('Done')