import numpy as np
import pandas as pd
import pickle

url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
main_df = pd.read_csv(url)

# datasets = {}
# for location in np.unique(main_df.location):
    # loc_df = main_df[main_df.location==location].copy()
    # df = pd.DataFrame(columns=("deaths", "vaccines"))
    # for date in np.unique(loc_df.date):
        # loc_date_df = loc_df[loc_df.date == date]
        # deaths = loc_date_df['total_deaths_per_million'].item()
        # vaccines = loc_date_df['people_vaccinated_per_hundred'].item()
        # df.loc[date] = [deaths, vaccines]
    # datasets[location] = df

datasets = {}
for location in np.unique(main_df.location):
    deaths = []
    vaccines = []
    loc_df = main_df[main_df.location==location].copy()

    # eliminate contries with small population:
    idx = -1
    try:
        while True:
            tc = loc_df.total_cases.iloc[idx]
            tcpm = loc_df.total_cases_per_million.iloc[idx]
            if not np.isnan(tc) and not np.isnan(tcpm):
                break
            idx -= 1
    except IndexError:
        continue
    pop_size_in_millions = tc/tcpm
    if pop_size_in_millions < 1:
        continue

    dates = np.unique(loc_df.date)
    for date in dates:
        loc_date_df = loc_df[loc_df.date == date]
        deaths.append(loc_date_df['total_deaths_per_million'].item())
        vaccines.append(loc_date_df['people_vaccinated_per_hundred'].item())

    df = pd.DataFrame({"deaths": deaths, "vaccines": vaccines})
    df.set_index(dates, inplace=True)
    df = df[np.logical_not(df.deaths.isna())]

    if not len(df):
        continue

    # de-accumulate deaths (i.e.: get daily deaths)
    for i in range(df.shape[0]-1, 0, -1):
        df.iloc[i, 0] = df.iloc[i, 0].item() - df.iloc[i - 1, 0].item()

    # if number of vaccine is NaN, then use previous day
    if np.isnan(df.iloc[0, 1]):
        df.iloc[0, 1] = 0
    for i in range(1, df.shape[0]):
        if np.isnan(df.iloc[i, 1]):
            df.iloc[i, 1] = df.iloc[i-1, 1].item()

    datasets[location] = df

with open("df.pkl", "wb") as f:
    pickle.dump(datasets, f)
