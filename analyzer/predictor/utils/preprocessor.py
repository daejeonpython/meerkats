import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def preprocess(file_in, file_out, target_disease):
        
    # 1. read raw data and extract desired columns
    df_raw = pd.read_csv(file_in, sep='\t')    
    # print(df.shape)    
    
    df_raw = df_raw[['발생일', '질병', '혈청형', '건수', '지역', '국가']]
    df_raw.rename(columns={'발생일': 'date', '질병': 'disease', '혈청형': 'serotype', '건수': 'outbreaks', '지역': 'region', '국가': 'country'}, inplace=True)
    df_raw['date'] = pd.to_datetime(df_raw['date'])
    df_raw.set_index('date', inplace=True)
    df_raw = df_raw.sort_values(by=['date'])        
    df_raw = df_raw[df_raw['disease'] == target_disease]
    print(df_raw.describe())

    # 2. Get time range between the first date and the last date    
    first_date = df_raw.index[0]
    last_date = df_raw.index[-1]
    time_series = pd.date_range(first_date, periods=(last_date - first_date).days)
    
    # 3. Make new dafaframe with respect to the region, i.e., five continents (Asia, Europe, America, Africa, Oceania)
    unique_values = df_raw['region'].unique()    
    df = pd.DataFrame(index=time_series, columns=unique_values)
    df.index.name = 'timestamp'    

    for time_point in time_series:
        rows = df_raw.loc[df_raw.index == time_point]                
        regions = rows.groupby(['region']).size().to_frame().T
                        
        for col in regions.columns:            
            df.loc[time_point][col] = regions.loc[0][col]

    df.rename(columns={'아시아': 'Asia', '아프리카': 'Africa', '아메리카': 'America', '유럽': 'Europe', '오세아니아': 'Oceania'}, inplace=True)        
    df.drop(columns=['None', 'Oceania'], inplace=True)  # remove Oceania to avoid data sparcity problem
    df.fillna(0, inplace=True)    
    print(df.describe())        

    # 4. Write dataframe to csv
    df.to_csv(file_out, sep='\t')

        
def verify(file_in, target_disease):
    
    df = csv_to_pd(file_in)

    for col in df.columns:
        plot(title=f'{target_disease}_{col}_plot', xlabel='timestamp', ylabel='number_of_outbreaks', x=df.index, y=df[col], save_path=os.path.join('data', f'{target_disease}_{col}.png'))

    plot(title=f'{target_disease}_altogether', xlabel='timestamp', ylabel='number_of_outbreaks', x=df.index, y=df[:], save_path=os.path.join('data', f'{target_disease}_altogether.png'))            
    plot(title=f'{target_disease}_sum', xlabel='timestamp', ylabel='number_of_outbreaks', x=df.index, y=df[:].sum(axis=1), save_path=os.path.join('data', f'{target_disease}_sum.png'))         


def csv_to_pd(data_path):
    
    df = pd.read_csv(data_path, sep='\t')    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df = df[df.index > '2017-01-01']   # start from 2017 to avoid data sparcity problem.
    
    return df  


def plot(title, xlabel, ylabel, x, y, save_path):
    plt.figure(figsize=(12,8))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.plot(x, y)
    plt.savefig(save_path)



if __name__ == '__main__':    
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_data', type=str, help='path to OIE csv data')
    parser.add_argument('--preprocessed_data', type=str, help='path to preprocessed data')    
    parser.add_argument('--target_disease', type=str, help='target disease to train & predict')
    # parser.add_argument('--count_by_row', action='store_true', help='increment y by a row or not')
    opt = parser.parse_args()

    preprocess(opt.raw_data, opt.preprocessed_data, opt.target_disease)    
    verify(opt.preprocessed_data, 'ASF')