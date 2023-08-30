import pandas as pd
import glob

FR_data = pd.read_pickle(r'CFR_data.pickle')


# Drop all duplicate records
FR_data.drop_duplicates(subset='CFR', keep='last', inplace=True)


# concatenate data for every month
for month in ['01','02','03','04','05','06','07','08','09','10','11','12']:
    path = f"MONICAP\\2021\\{month}"  # Replace with the actual directory path
    all_files = glob.glob(path + "/*.txt")

    dfs = []
    for file in all_files:
        df = pd.read_csv(file, delimiter='\t', header=None, names=['Name', 'CFR', 'GDH', 'lat', 'lon', 'heading', 'speed'])
        df = df.dropna(subset=['GDH']) #delete values that do not possess valid GDH
        df['day'] = [int(day[0:2]) for day in df.GDH] # save the day

        # Merge df and FR_data based on 'Registration Number'
        merged_df = df.merge(FR_data, on='CFR', how='left') # merge with FR data based on CFR registry

        # Create a new column 'Gear' in df with the value of 'Main fishing gear' and LOA
        df['Gear'] = merged_df['Main fishing gear']
        df['LOA'] = merged_df['LOA']


        #df = df[df.speed<3]
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    df.to_csv('MONICAP\\Monthly\\'+path.split('\\')[0]+'_'+path.split('\\')[1]+'_'+path.split('\\')[2]+'.csv')

    print(month)