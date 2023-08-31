import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import contextily as ctx
import pandas as pd
import numpy as np

# Define the output directory for saving the plots
output_dir = 'saved_shapefiles'

# Read the shapefile
shapefile_path = 'shapefiles/algarve_polygons.shp'
algarve_polygons = gpd.read_file(shapefile_path)

# Read the shapefile for the Portuguese sea
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)

df_all = pd.DataFrame()

# Iterate over each month
for month in range(1, 13):
    # Format the month value with leading zeros
    month_str = f'{month:02d}'
    print(month_str)

    df = pd.read_csv(f'MONICAP\Monthly\MONICAP_2021_{month_str}.csv')

    df_all = df_all.append(df, ignore_index=True)



df_all.drop(columns='Unnamed: 0', inplace=True)

df_all.drop_duplicates(inplace=True)

df_all.dropna(subset=['Gear'], inplace=True)

art_level = {'NK':1, 'GND':5 , 'DRH':5 , 'LTL':5, 'LLD' :5 , 'PS':9 , 'FPO':6 , 'OTB':9, 'GNS':6, 'LLS':5, 'LHP':4, 'DRB':7, 'GTR':8, 'SB':8, 'PTB':9, 'LNB':9}

df_all['art_level'] = [art_level[gear] for gear in df_all.Gear]

list_all1 = df_all.CFR.unique()

df_all = df_all[df_all.speed<5]

# Add 'month' and 'year' columns
df_all['month'] = df_all['GDH'].str.split('/').str[1].astype(int)
df_all['year'] = df_all['GDH'].str.split('/').str[2].str.split().str[0].astype(int)

list_slow1 = df_all.CFR.unique()

left_over1 = list(set(list_all1) - set(list_slow1))


# First, sort the DataFrame by 'CFR' and 'month'
df_all_sorted = df_all.sort_values(by=['CFR', 'month'])

# Group by 'month' and then get the unique count of 'CFR'
unique_cfrs_per_month = df_all_sorted.groupby('month')['CFR'].nunique()

# Display the results
print(unique_cfrs_per_month)

list_slow_gear = df_all.Gear.unique()


# Drop duplicates based on both 'CFR' and 'Gear' to count each 'Gear' only once for each unique combination of 'CFR' and 'Gear' in each month
unique_cfr_gear_month_df = df_all.drop_duplicates(subset=['CFR', 'Gear', 'month'])

# Count occurrences of each 'Gear' after the duplicates have been dropped for each month
gear_counts_by_month = unique_cfr_gear_month_df.groupby('month')['Gear'].value_counts()
gear_counts_for_may = gear_counts_by_month.loc[5]
# Display the resulting gear_counts_by_month Series
print(gear_counts_by_month)


#Anual

# Drop duplicates based on 'CFR' to count each 'Gear' only once for each 'CFR' number
unique_cfr_df = df_all.drop_duplicates(subset='CFR')

# Count occurrences of each 'Gear' after the duplicates have been dropped
gear_counts = unique_cfr_df['Gear'].value_counts()

# Display the resulting gear_counts Series
print(gear_counts)




def enumerate_gears_per_month(gear_counts_by_month):
    month_names = ["January", "February", "March", "April", "May", "June", 
                   "July", "August", "September", "October", "November", "December"]

    for month in range(1, 13):
        gears_for_month = gear_counts_by_month[month].index.tolist() if month in gear_counts_by_month else []
        
        # Print out the month name followed by the gear types used
        print(f"\n{month_names[month-1]}:")
        for idx, gear in enumerate(gears_for_month, start=1):
            print(f"{idx}. {gear}")

# Call the function to display the results
enumerate_gears_per_month(gear_counts_by_month)






import pandas as pd

# Assuming df_all is already defined, if not, define it
df_all = pd.DataFrame()

for month in range(1, 12):  # Excluding December
    # Format the month value with leading zeros
    month_str = f'{month:02d}'
    print(month_str)
    
    df = pd.read_csv(f'MONICAP\Monthly\MONICAP_2022_{month_str}.csv')

    # Drop rows with faulty date formats
    df = df[df['GDH'].str.match(r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$')]

    # Convert 'GDH' column to datetime format
    df['GDH'] = pd.to_datetime(df['GDH'], format='%d/%m/%Y %H:%M:%S')
    
    # Filter rows with year 2022
    df = df[df['GDH'].dt.year == 2022]

    df_all = df_all.append(df, ignore_index=True)


df_all.drop(columns='Unnamed: 0', inplace=True)

df_all.drop_duplicates(inplace=True)

df_all.dropna(subset=['Gear'], inplace=True)

art_level = {'NK':1, 'GND':5 , 'DRH':5 , 'LTL':5, 'LLD' :5 , 'PS':9 , 'FPO':6 , 'OTB':9, 'GNS':6, 'LLS':5, 'LHP':4, 'DRB':7, 'GTR':8, 'SB':8, 'PTB':9, 'LNB':9}

df_all['art_level'] = [art_level[gear] for gear in df_all.Gear]

list_all = df_all.CFR.unique()

df_all = df_all[df_all.speed<5]

# Add 'month' and 'year' columns
df_all['month'] = df_all['GDH'].dt.month
df_all['year'] = df_all['GDH'].dt.year

list_slow = df_all.CFR.unique()

left_over = list(set(list_all) - set(list_slow))


# First, sort the DataFrame by 'CFR' and 'month'
df_all_sorted = df_all.sort_values(by=['CFR', 'month'])

# Group by 'month' and then get the unique count of 'CFR'
unique_cfrs_per_month = df_all_sorted.groupby('month')['CFR'].nunique()

# Display the results
print(unique_cfrs_per_month)

list_slow_gear = df_all.Gear.unique()


# Drop duplicates based on both 'CFR' and 'Gear' to count each 'Gear' only once for each unique combination of 'CFR' and 'Gear' in each month
unique_cfr_gear_month_df = df_all.drop_duplicates(subset=['CFR', 'Gear', 'month'])

# Count occurrences of each 'Gear' after the duplicates have been dropped for each month
gear_counts_by_month = unique_cfr_gear_month_df.groupby('month')['Gear'].value_counts()

# Display the resulting gear_counts_by_month Series
print(gear_counts_by_month)




#Anual_Gear
# Drop duplicates based on 'CFR' to count each 'Gear' only once for each 'CFR' number
unique_cfr_df = df_all.drop_duplicates(subset='CFR')

# Count occurrences of each 'Gear' after the duplicates have been dropped
gear_counts = unique_cfr_df['Gear'].value_counts()

# Display the resulting gear_counts Series
print(gear_counts)


# Convert lists to sets
set_slow1 = set(list_slow1)
set_slow = set(list_slow)

# Find the intersection of the two sets
common_cfrs = set_slow1.intersection(set_slow)

# Print the count of common CFRs
print(f"Number of CFRs that appear in both list_slow1 and list_slow: {len(common_cfrs)}")










import pandas as pd
import matplotlib.pyplot as plt

# Ler os dados fiscrep
fiscrep_data = pd.read_csv('fiscrep_algarve.csv')

# Filtrar os dados para 2021 e 2022 excluindo dezembro de 2022
filtered_data = fiscrep_data[((fiscrep_data['year'] == 2021) | ((fiscrep_data['year'] == 2022) & (fiscrep_data['month'] != 12)))]

# Agrupar e contar ações de fiscalização por mês e ano
grouped_data = filtered_data.groupby(['year', 'month']).size().reset_index(name='count')

# Plotar os dados
plt.figure(figsize=(12, 6))
for year in [2021, 2022]:
    monthly_counts = grouped_data[grouped_data['year'] == year]
    plt.plot(monthly_counts['month'], monthly_counts['count'], label=f'Ano {year}', marker='o')
    
    # Adicionar o número total de ações para cada mês acima do ponto correspondente
    for _, row in monthly_counts.iterrows():
        plt.annotate(str(row['count']), (row['month'], row['count'] + 2), ha='center')

plt.title("Ações de Fiscalização FISCREP por Mês (2021 e 2022)")
plt.xlabel("Mês")
plt.ylabel("Número de Ações")
plt.xticks(range(1, 13), ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
plt.legend()
plt.grid(True, which="both", ls="--")
plt.tight_layout()
plt.show()




#LOA MONTH AND YEAR
import pandas as pd
import matplotlib.pyplot as plt

# Ler os dados fiscrep
fiscrep_data = pd.read_csv('fiscrep_algarve.csv')

# Filtrar os dados para 2021 e 2022 excluindo dezembro de 2022
filtered_data = fiscrep_data[((fiscrep_data['year'] == 2021) | ((fiscrep_data['year'] == 2022) & (fiscrep_data['month'] != 12)))]

# Agrupar e calcular a média de 'LOA' por mês e ano
grouped_data = filtered_data.groupby(['year', 'month'])['LOA'].mean().reset_index(name='avg_LOA')

# Plotar os dados
plt.figure(figsize=(12, 6))
for year in [2021, 2022]:
    monthly_avg_LOA = grouped_data[grouped_data['year'] == year]
    plt.plot(monthly_avg_LOA['month'], monthly_avg_LOA['avg_LOA'], label=f'Ano {year}', marker='o')
    # Adicionar a média de 'LOA' para cada mês acima do ponto correspondente
    for _, row in monthly_avg_LOA.iterrows():
        plt.annotate(f"{row['avg_LOA']:.2f}", (row['month'], row['avg_LOA'] + 0.2), ha='center')

plt.title("Média de LOA por Mês (2021 e 2022) - FISCREP")
plt.xlabel("Mês")
plt.ylabel("Média de LOA (metros)")
plt.xticks(range(1, 13), ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
plt.legend()
plt.grid(True, which="both", ls="--")
plt.tight_layout()
plt.show()



import pandas as pd
import matplotlib.pyplot as plt

# Create empty dataframe to store aggregated results
all_data = pd.DataFrame(columns=['year', 'month', 'LOA'])

# Loop through the months and years to load data, preprocess, and append to all_data
for year in [2021, 2022]:
    for month in range(1, 13):
        if year == 2022 and month == 12:
            continue
        df = pd.read_csv(f'MONICAP\Monthly\MONICAP_{year}_{str(month).zfill(2)}.csv')
        
        # Clean the data
        df.drop(columns='Unnamed: 0', inplace=True)
        df.drop_duplicates(inplace=True)
        df.dropna(subset=['Gear'], inplace=True)
        
        # Filter rows with speed < 5
        df = df[df.speed < 5]
        
        # Append the relevant columns to all_data
        all_data = all_data.append(df[['LOA']].assign(year=year, month=month))

# Group by month and year and calculate average 'LOA'
grouped_data = all_data.groupby(['year', 'month'])['LOA'].mean().reset_index(name='avg_LOA')

# Plotting
plt.figure(figsize=(12, 6))
for year in [2021, 2022]:
    monthly_avg_LOA = grouped_data[grouped_data['year'] == year]
    plt.plot(monthly_avg_LOA['month'], monthly_avg_LOA['avg_LOA'], label=f'Ano {year}', marker='o')
    # Add LOA average for each month above the respective point
    for _, row in monthly_avg_LOA.iterrows():
        plt.annotate(f"{row['avg_LOA']:.2f}", (row['month'], row['avg_LOA'] + 0.2), ha='center')

plt.title("Média de LOA por Mês (2021 e 2022) - MONICAP")
plt.xlabel("Mês")
plt.ylabel("Média de LOA (metros)")
plt.xticks(range(1, 13), ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
plt.legend()
plt.grid(True, which="both", ls="--")
plt.tight_layout()
plt.show()





import pandas as pd
import matplotlib.pyplot as plt

# Ler os dados fiscrep
fiscrep_data = pd.read_csv('fiscrep_algarve.csv')

# Filtrar os dados para 2021 e 2022 excluindo dezembro de 2022
filtered_data = fiscrep_data[((fiscrep_data['year'] == 2021) | ((fiscrep_data['year'] == 2022) & (fiscrep_data['month'] != 12)))]

# Pegar valores únicos da coluna 'Gear'
unique_gears = filtered_data['Gear'].unique()

# Criar um gráfico de barras separado para cada valor único de 'Gear'
for gear in unique_gears:
    gear_data = filtered_data[filtered_data['Gear'] == gear]
    
    # Agrupar e contar ações de fiscalização por mês e ano para o valor atual de 'Gear'
    grouped_data = gear_data.groupby(['year', 'month']).size().reset_index(name='count')
    
    # Plotar os dados
    plt.figure(figsize=(12, 6))
    
    # Largura da barra
    width = 0.4
    months = range(1, 13)
    
    for year in [2021, 2022]:
        # Deslocamento para separar barras de diferentes anos
        offset = -width/2 if year == 2021 else width/2
        
        monthly_counts = grouped_data[grouped_data['year'] == year]
        
        # Gráfico de barras
        plt.bar(monthly_counts['month'] + offset, monthly_counts['count'], width=width, label=f'Ano {year}')
        
        # Adicionar o número total de ações para cada mês acima da barra correspondente
        for _, row in monthly_counts.iterrows():
            plt.annotate(str(row['count']), (row['month'] + offset, row['count'] + 2), ha='center')
    
    plt.title(f"Ações de Fiscalização FISCREP por Mês (2021 e 2022) para Gear = {gear}")
    plt.xlabel("Mês")
    plt.ylabel("Número de Ações")
    plt.xticks(months, ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
    plt.legend()
    plt.grid(axis='y', which="both", ls="--")
    plt.tight_layout()
    plt.show()


import pandas as pd
import matplotlib.pyplot as plt

# Ler os dados fiscrep
fiscrep_data = pd.read_csv('fiscrep_algarve.csv')

# Filtrar os dados para 2021 e 2022 excluindo dezembro de 2022
filtered_data = fiscrep_data[((fiscrep_data['year'] == 2021) | ((fiscrep_data['year'] == 2022) & (fiscrep_data['month'] != 12)))]

# Pegar valores únicos da coluna 'Gear'
unique_gears = filtered_data['Gear'].unique()

# Criar um gráfico de barras separado para cada valor único de 'Gear'
for gear in unique_gears:
    gear_data = filtered_data[filtered_data['Gear'] == gear]
    
    # Agrupar e contar ações de fiscalização por mês e ano para o valor atual de 'Gear'
    grouped_data = gear_data.groupby(['year', 'month']).size().reset_index(name='count')
    
    # Plotar os dados
    plt.figure(figsize=(12, 6))
    
    # Largura da barra
    width = 0.4
    months = range(1, 13)
    
    for year in [2021, 2022]:
        # Deslocamento para separar barras de diferentes anos
        offset = -width/2 if year == 2021 else width/2
        
        monthly_counts = grouped_data[grouped_data['year'] == year]
        
        # Gráfico de barras
        plt.bar(monthly_counts['month'] + offset, monthly_counts['count'], width=width, label=f'Ano {year}')
        
        # Adicionar o número total de ações para cada mês acima da barra correspondente
        for _, row in monthly_counts.iterrows():
            plt.annotate(str(row['count']), (row['month'] + offset, row['count'] + 2), ha='center')
    
    plt.title(f"Ações de Fiscalização FISCREP por Mês (2021 e 2022) para Gear = {gear}")
    plt.xlabel("Mês")
    plt.ylabel("Número de Ações")
    plt.xticks(months, ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
    plt.legend()
    plt.grid(axis='y', which="both", ls="--")
    plt.tight_layout()
    plt.show()







import pandas as pd


# 1. Carregar os dados
df_2022 = pd.read_csv(f'MONICAP\Monthly\MONICAP_2022_{month}.csv')
df_2021 = pd.read_csv(f'MONICAP\Monthly\MONICAP_2021_{month}.csv')

# 2. Limpar os dados
for df in [df_2022, df_2021]:
    df.drop(columns='Unnamed: 0', inplace=True)
    df.drop_duplicates(inplace=True)
    df.dropna(subset=['Gear'], inplace=True)

# 3. Filtrar linhas com velocidade inferior a 5
df_2022 = df_2022[df_2022.speed < 5]
df_2021 = df_2021[df_2021.speed < 5]

# 4. Carregar dados fiscrep
fiscrep_data = pd.read_csv('fiscrep_algarve.csv')

# Normalizar os nomes: remover espaços em branco e converter para minúsculas
df_2022['Name'] = df_2022['Name'].str.strip().str.lower()
df_2021['Name'] = df_2021['Name'].str.strip().str.lower()
fiscrep_data['Name'] = fiscrep_data['Name'].str.strip().str.lower()

# 5. Verificar os nomes comuns entre os conjuntos de dados
common_names_2022 = set(df_2022['Name']).intersection(set(fiscrep_data['Name']))
common_names_2021 = set(df_2021['Name']).intersection(set(fiscrep_data['Name']))

print(f"Common names for 2022: {common_names_2022}")
print(f"Common names for 2021: {common_names_2021}")












import pandas as pd

# Initialize a dictionary to store results
results = {}

# Loop through each year and month
for year in [2021, 2022]:
    for month in range(1, 13):  # From January (1) to December (12)
        month_str = str(month).zfill(2)  # Convert to 2-digit string
        
        # Load data
        df = pd.read_csv(f'MONICAP\Monthly\MONICAP_{year}_{month_str}.csv')
        
        # Clean the data
        df.drop(columns='Unnamed: 0', inplace=True)
        df.drop_duplicates(inplace=True)
        df.dropna(subset=['Gear'], inplace=True)

        # Filter rows with speed less than 5
        df = df[df.speed < 5]

        # Normalize the names
        df['Name'] = df['Name'].str.strip().str.lower()
        fiscrep_data['Name'] = fiscrep_data['Name'].str.strip().str.lower()  # We can move this out of the loop if fiscrep_data doesn't change
        
        # Find common names
        common_names = set(df['Name']).intersection(set(fiscrep_data['Name']))
        
        # Store the results
        results[f"{year}_{month_str}"] = common_names

# Print the results
for key, value in results.items():
    print(f"Common names for {key}: {value}")




import pandas as pd

# Initialize a dictionary to store results
results = {}

# Load fiscrep data once since it's constant across the loop
fiscrep_data = pd.read_csv('fiscrep_algarve.csv')
fiscrep_data['Name'] = fiscrep_data['Name'].str.strip().str.lower()

# Loop through each year and month
for year in [2021, 2022]:
    for month in range(1, 13):  # From January (1) to December (12)
        month_str = str(month).zfill(2)  # Convert to 2-digit string
        
        # Load data
        df = pd.read_csv(f'MONICAP\Monthly\MONICAP_{year}_{month_str}.csv')
        
        # Clean the data
        df.drop(columns='Unnamed: 0', inplace=True)
        df.drop_duplicates(inplace=True)
        df.dropna(subset=['Gear'], inplace=True)

        # Filter rows with speed less than 5
        df = df[df.speed < 5]

        # Normalize the names
        df['Name'] = df['Name'].str.strip().str.lower()
        
        # Find and count common names
        common_names_count = len(set(df['Name']).intersection(set(fiscrep_data['Name'])))
        
        # Store the results
        results[f"{year}_{month_str}"] = common_names_count

# Print the results
for key, value in results.items():
    print(f"Number of common names for {key}: {value}")




# Dictionary to store 'Gear' values for each name
gear_per_name = {}

# Loop through the fiscrep_data
for index, row in fiscrep_data.iterrows():
    name = row['Name']
    if name not in gear_per_name:
        gear_per_name[name] = []

# Loop through each year and month again
for year in [2021, 2022]:
    for month in range(1, 13):  # From January (1) to December (12)
        month_str = str(month).zfill(2)  # Convert to 2-digit string
        
        # Load data
        df = pd.read_csv(f'MONICAP\Monthly\MONICAP_{year}_{month_str}.csv')
        
        # Clean the data
        df.drop(columns='Unnamed: 0', inplace=True)
        df.drop_duplicates(inplace=True)
        df.dropna(subset=['Gear'], inplace=True)

        # Filter rows with speed less than 5
        df = df[df.speed < 5]

        # Normalize the names
        df['Name'] = df['Name'].str.strip().str.lower()
        
        # Add 'Gear' values for each name
        for index, row in df.iterrows():
            name = row['Name']
            gear = row['Gear']
            if name in gear_per_name and gear not in gear_per_name[name]:
                gear_per_name[name].append(gear)

# Print the 'Gear' values for each name
for name, gears in gear_per_name.items():
    print(f"'Gear' for {name}: {', '.join(gears)}")

# Print the 'Gear' values for only those names that have non-empty gear lists
for name, gears in gear_per_name.items():
    if gears:  # Checks if the gear list is non-empty
        print(f"'Gear' for {name}: {', '.join(gears)}")


# Dictionary to count the number of occurrences for each 'Arte' (gear type)
arte_counts = {}

# Go through each name's list of gears
for name, gears in gear_per_name.items():
    for gear in gears:
        if gear in arte_counts:
            arte_counts[gear] += 1
        else:
            arte_counts[gear] = 1

# Print the counts for each 'Arte'
for arte, count in arte_counts.items():
    print(f"'{arte}': {count} occurrences")



# Dictionary to count the number of occurrences for each 'Arte' (gear type) for each year
arte_counts_by_year = {2021: {}, 2022: {}}

# Loop through each year and month again
for year in [2021, 2022]:
    for month in range(1, 13):  # From January (1) to December (12)
        month_str = str(month).zfill(2)  # Convert to 2-digit string
        
        # Load data
        df = pd.read_csv(f'MONICAP\Monthly\MONICAP_{year}_{month_str}.csv')
        
        # Clean the data
        df.drop(columns='Unnamed: 0', inplace=True)
        df.drop_duplicates(inplace=True)
        df.dropna(subset=['Gear'], inplace=True)

        # Filter rows with speed less than 5
        df = df[df.speed < 5]

        # Normalize the names
        df['Name'] = df['Name'].str.strip().str.lower()
        
        # Add 'Gear' values for each name and count the occurrences for the year
        for index, row in df.iterrows():
            name = row['Name']
            gear = row['Gear']
            if name in gear_per_name:
                if gear not in gear_per_name[name]:
                    gear_per_name[name].append(gear)
                # Count occurrences for the year
                if gear in arte_counts_by_year[year]:
                    arte_counts_by_year[year][gear] += 1
                else:
                    arte_counts_by_year[year][gear] = 1

# Print the counts for each 'Arte' separated by year
for year, counts in arte_counts_by_year.items():
    print(f"\nYear: {year}")
    for arte, count in counts.items():
        print(f"'{arte}': {count} occurrences")



import pandas as pd

# Create an empty DataFrame to store data across all months and years
all_data = pd.DataFrame()

# Loop through each year and month
for year in [2021, 2022]:
    for month in range(1, 13):  # From January (1) to December (12)
        month_str = str(month).zfill(2)  # Convert to 2-digit string
        
        # Load data
        df = pd.read_csv(f'MONICAP\Monthly\MONICAP_{year}_{month_str}.csv')
        
        # Clean the data
        df.drop(columns='Unnamed: 0', inplace=True)
        df.drop_duplicates(inplace=True)
        df.dropna(subset=['Gear'], inplace=True)

        # Filter rows with speed less than 5
        df = df[df.speed < 5]
        
        # Append to the all_data DataFrame
        all_data = all_data.append(df)

# Add a 'year' column to the all_data DataFrame
all_data['year'] = pd.DatetimeIndex(all_data['date']).year  # Assuming you have a 'date' column to extract the year

# Dictionary to store the results
gear_count_per_CFR_per_year = {2021: {}, 2022: {}}

# Loop through each year
for year in [2021, 2022]:
    # Filter data for the current year
    yearly_data = all_data[all_data['year'] == year]
    
    # Group by 'CFR' and apply a function to get unique gears
    unique_gears_per_CFR = yearly_data.groupby('CFR')['Gear'].unique().apply(len)
    
    # Count the number of CFRs having each number of unique gears
    gear_counts = unique_gears_per_CFR.value_counts().to_dict()
    
    # Update the results dictionary
    gear_count_per_CFR_per_year[year] = gear_counts

print(gear_count_per_CFR_per_year)




import pandas as pd

# Create an empty DataFrame to store data across all months and years
all_data = pd.DataFrame()

# Loop through each year and month
for year in [2021, 2022]:
    for month in range(1, 13):  # From January (1) to December (12)
        month_str = str(month).zfill(2)  # Convert to 2-digit string
        
        # Load data
        df = pd.read_csv(f'MONICAP\Monthly\MONICAP_{year}_{month_str}.csv')
        
        # Clean the data
        df.drop(columns='Unnamed: 0', inplace=True)
        df.drop_duplicates(inplace=True)
        df.dropna(subset=['Gear'], inplace=True)

        # Filter rows with speed less than 5
        df = df[df.speed < 5]
        
        # Append to the all_data DataFrame
        all_data = all_data.append(df)

# Extract the 'year' from 'GDH' column
all_data['year'] = pd.to_datetime(all_data['GDH'], format='%d/%m/%Y %H:%M:%S').dt.year

# Dictionary to store the results
gear_count_per_year = {}

# Loop through each year
for year in [2021, 2022]:
    # Filter data for the current year
    yearly_data = all_data[all_data['year'] == year]
    
    # Group by 'Gear' and 'CFR' to find unique 'CFR' for each 'Gear'
    unique_CFRs_per_gear = yearly_data.groupby('Gear')['CFR'].unique().apply(len)
    
    # Convert the result to dictionary and store in gear_count_per_year
    gear_count_per_year[year] = unique_CFRs_per_gear.to_dict()

print(gear_count_per_year)

