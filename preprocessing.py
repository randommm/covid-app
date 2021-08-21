import numpy as np
import pandas as pd
import pickle
from collections import Counter, OrderedDict

url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
#url = 'owid-covid-data.csv'
rec_df = pd.read_csv(url)

rec_df = rec_df[rec_df.iso_code.agg(len)==3]
rec_df.rename(columns = {
    'total_deaths_per_million': 'deaths',
    'people_vaccinated_per_hundred': 'vaccines',
    'people_fully_vaccinated_per_hundred': 'fvaccines',
    }, inplace = True)

main_df = ['deaths', 'vaccines', 'fvaccines', 'location', 'date']
main_df = rec_df[main_df].copy()
for location in np.unique(main_df.location):
    df = main_df[main_df.location==location].copy()
    dates = np.unique(df.date)

    if all(df.deaths.isna()):
        print("Removing location", location, "as all deaths are nan")
        main_df = main_df[main_df.location!=location]
        continue

    if all(df.vaccines.isna()):
        print("Removing location", location, "as all vaccines are nan")
        main_df = main_df[main_df.location!=location]
        continue

    # de-accumulate deaths (i.e.: get daily deaths)
    for i in range(df.shape[0]-1, 0, -1):
        ci = np.where(df.columns == 'deaths')[0].item()
        past = df.iloc[i - 1, ci].item()
        if np.isnan(past):
            continue
        df.iloc[i, ci] = df.iloc[i, ci].item() - past

    # if number of vaccine is NaN, then use previous day
    for cname in ['vaccines', 'fvaccines']:
        ci = np.where(df.columns == cname)[0].item()
        if np.isnan(df.iloc[0, ci]):
            df.iloc[0, ci] = 0
        for i in range(1, df.shape[0]):
            if np.isnan(df.iloc[i, ci]):
                df.iloc[i, ci] = df.iloc[i-1, ci].item()

    main_df[main_df.location==location] = df

with open("main_df.pkl", "wb") as f:
    pickle.dump(main_df, f)

locations = rec_df.location.unique()
df_vars = []
for location in locations:
    dfl = rec_df[rec_df.location==location].copy()
    dfl.pop('location')
    dfld = dict(location=location)
    for column in dfl.columns:
        if len(Counter(dfl[column])) == 1 and not dfl[column].iloc[[0]].isna().item():
            dfld[column] = dfl[column].iloc[0]
    df_vars.append(dfld)
df_vars = pd.DataFrame(df_vars)


with open("df_vars.pkl", "wb") as f:
    pickle.dump(df_vars, f)
