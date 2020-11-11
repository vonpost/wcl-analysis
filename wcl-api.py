import json
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
pages = [filename for filename in os.listdir('.') if filename.startswith("page")]

all_reports = []
for page in pages:
    with open(page) as f:
        json_reports = json.load(f)
        f.close()
    reports = json_reports['data']['worldData']['encounter']['characterRankings']
    reports = pd.json_normalize(data=reports, record_path=['rankings','gear'], meta=[['rankings', 'amount'],['rankings', 'name'],['rankings', 'duration']])
    # Now we are only interested in the 15th slot which is the main hand
    reports = reports.iloc[15::18,:]
    # We can drop some irrelevant columns
    wanted_columns = ['name','id','rankings.amount','rankings.name','rankings.duration']
    reports = reports[wanted_columns]
    all_reports.append(reports)

# Now we need to get the weapon speed of each item. We get a json-database of items.
reports = pd.concat(all_reports)
with open('./item_data.json') as f:
    json_items = json.load(f)
    f.close()
items = pd.json_normalize(json_items)
# We filter out only the weapons and rename itemId to id so it can be merged with report.
# Since the weapon speed is contained in the tooltip we need to keep that as well.
weapons = items[items['class'] == 'Weapon']
weapons = weapons.rename(columns={'itemId':'id'})
weapons = weapons[['id','tooltip']]
# We need to drop Elune's candle since it has no speed.
weapons = weapons.drop(index=weapons[weapons.id == 21713].index)
# Then we extract the speeds.
def format_label(label):
    speed = label[6:]
    if(len(speed) > 0):
        return float(speed)
    else:
        return np.nan
extract_speed = lambda tooltips : [format_label(t['label']) for t in tooltips if 'Speed ' in t['label']][0]
weapons.tooltip = weapons.tooltip.apply(extract_speed)
weapons = weapons.rename(columns={'tooltip':'speed'})

# Then we merge it with the reports, so now we have a dps measure and main hand weapon speed for each player in the top rankings.
# We need to make sure that the dps is in right format as well.
reports = reports.rename(columns={'rankings.amount':'dps', 'rankings.duration':'duration'})
reports.dps = reports.dps.apply(float)
reports.duration = reports.duration.apply(float)
reports = reports.dropna()
reports.id = reports.id.apply(int)
reports = reports.merge(weapons)
plt.figure()
sns.boxplot(data=reports, x='speed', y='dps')
plt.savefig("lala")
plt.close()
