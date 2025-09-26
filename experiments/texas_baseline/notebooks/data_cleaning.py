import pandas as pd
import matplotlib.pyplot as plt

# flu data
flu_raw = pd.read_csv("ILINet_tx.csv", header=None)  
print(flu_raw.head(20))

# first row as header
flu = pd.read_csv("ILINet_tx.csv", header=0)

# Convert YEAR + WEEK into proper datetime (Monday of that week)
flu['date'] = pd.to_datetime(flu['YEAR'].astype(str) + flu['WEEK'].astype(str) + '1', format='%G%V%u')

# only important columns
flu_clean = flu[['date', '%UNWEIGHTED ILI', 'ILITOTAL', 'TOTAL PATIENTS']].copy()

# Rename
flu_clean.rename(columns={
    '%UNWEIGHTED ILI': 'flu_percent',
    'ILITOTAL': 'ili_total',
    'TOTAL PATIENTS': 'total_patients'
}, inplace=True)

flu_clean.to_csv("flu_tx_clean.csv", index=False)

print(flu_clean.head())


# mobility file
mobility = pd.read_csv("tx_mobility.csv")
print(mobility.head())
print(mobility.columns)
print(mobility['date'].min(), mobility['date'].max())

mobility_tx = mobility[mobility['sub_region_1'] == "Texas"].copy()

# only numeric columns aggregating
mobility_tx = (
    mobility.groupby("date")
    [["retail", "grocery", "parks", "transit", "workplaces", "residential"]]
    .mean()
    .reset_index()
)

print(mobility_tx.head(10))
print(mobility_tx.isna().sum())

# Convert date column
mobility_tx['date'] = pd.to_datetime(mobility_tx['date'])
mobility_tx = mobility_tx.set_index('date')

# Resample to weekly averages (weeks start on Monday)
weekly_mobility = (
    mobility_tx.resample('W-MON').mean().reset_index()
)

# Add year and week number
weekly_mobility['year'] = weekly_mobility['date'].dt.isocalendar().year
weekly_mobility['week'] = weekly_mobility['date'].dt.isocalendar().week

weekly_mobility.to_csv("mobility_tx_clean.csv", index=False)

print(weekly_mobility.head(10))

# Temp file/data
temp = pd.read_csv("Temp_tx.csv")

print(temp.head())    
print(temp.columns)  

temp = pd.read_csv("Temp_tx.csv")

# Convert YYYYMM -> datetime (first day of month)
temp['date'] = pd.to_datetime(temp['Date'], format='%Y%m')

# Rename columns
temp = temp.rename(columns={'Value':'avg_temp'})

# Expand to weekly by forward filling across each month
# full weekly date range from min to max
weekly_dates = pd.date_range(start=temp['date'].min(), end=temp['date'].max(), freq='W-MON')
weekly_temp = pd.DataFrame({'date': weekly_dates})

# merge monthly values into weekly, forward-fill
weekly_temp = pd.merge_asof(
    weekly_temp.sort_values('date'),
    temp[['date','avg_temp']].sort_values('date'),
    on='date'
)

# extract year + week
weekly_temp['year'] = weekly_temp['date'].dt.isocalendar().year
weekly_temp['week'] = weekly_temp['date'].dt.isocalendar().week

weekly_temp.to_csv("temp_tx_clean.csv", index=False)

print(weekly_temp.head(10))


# Merging cleaned files

flu = pd.read_csv("flu_tx_clean.csv")
mob = pd.read_csv("mobility_tx_clean.csv")
temp = pd.read_csv("temp_tx_clean.csv")

# is date datetime
flu['date'] = pd.to_datetime(flu['date'])
mob['date'] = pd.to_datetime(mob['date'])
temp['date'] = pd.to_datetime(temp['date'])

# year + week to flu if missing
if 'year' not in flu.columns or 'week' not in flu.columns:
    flu['year'] = flu['date'].dt.isocalendar().year
    flu['week'] = flu['date'].dt.isocalendar().week

#  mobility
if 'year' not in mob.columns or 'week' not in mob.columns:
    mob['year'] = mob['date'].dt.isocalendar().year
    mob['week'] = mob['date'].dt.isocalendar().week

#  temp
if 'year' not in temp.columns or 'week' not in temp.columns:
    temp['year'] = temp['date'].dt.isocalendar().year
    temp['week'] = temp['date'].dt.isocalendar().week

# Merge flu + mobility first
merged = pd.merge(flu, mob, on=['date','year','week'], how='outer')

# Merge temp 
merged = pd.merge(merged, temp, on=['date','year','week'], how='outer')

# Sort by date
merged = merged.sort_values('date').reset_index(drop=True)

# final merged dataset
merged.to_csv("predictus_tx_merged.csv", index=False)

print("Final merged dataset shape:", merged.shape)
print(merged.head(15))

print(merged.dropna().head(15))
print("First full data point:", merged.dropna().date.min())
print("Last full data point:", merged.dropna().date.max())


# Plot
plt.figure(figsize=(12,6))

plt.plot(merged['date'], merged['flu_percent'], label='Flu %', color='red')
plt.plot(merged['date'], merged['avg_temp'], label='Temp (F)', color='blue')
plt.plot(merged['date'], merged['retail'], label='Retail Mobility', color='green')

plt.legend()
plt.title("Texas Weekly: Flu %, Temperature, Mobility")
plt.xlabel("Date")
plt.ylabel("Value")
plt.grid(True)
plt.show()
