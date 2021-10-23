import os
import argparse
import pandas as pd
from utils.plots import plot
import datetime


def preprocess(file_in, file_out, target_disease, spatial_resolution, target_location, count_by_outbreaks):
        
    # 1. read raw data and extract desired columns
    df_raw = pd.read_csv(file_in, sep='\t')            
    df_raw = df_raw[['발생일', '질병', '혈청형', '건수', '지역', '국가']]
    df_raw.rename(columns={'발생일': 'date', '질병': 'disease', '혈청형': 'serotype', '건수': 'outbreaks', '지역': 'region', '국가': 'country'}, inplace=True)
    df_raw['date'] = pd.to_datetime(df_raw['date'])
    df_raw.set_index('date', inplace=True)
    df_raw = df_raw.sort_values(by=['date'])        
    df_raw = df_raw[df_raw['disease'] == target_disease]
    print(f'Raw data statistics:\n{df_raw.describe()}\n')

    # 2. Get time range between the first date and YESTERDAY
    first_date = df_raw.index[0]        
    today = datetime.datetime.now()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)    
    time_series = pd.date_range(first_date, periods=(today - first_date).days)
    
    # 3. Make new dafaframe with respect to the spatial resolution
    # ex) continents (Asia, Europe, America, Africa, Oceania) or countries (Korea, Japan, China, Russia)    
    target_location = target_location.split(',')    
    df = pd.DataFrame(index=time_series, columns=target_location)  # make new dataframe with columns of unique values            
    df.index.name = 'timestamp'

    for time_point in time_series:   
        
        # for each time_point (ex 2016-03-04), return every row that matches the time_point from raw dataframe                   
        rows = df_raw.loc[df_raw.index == time_point]        
        
        if count_by_outbreaks:  # count by number of outbreaks
            for column in target_location:
                outbreaks = pd.Series(rows[rows[spatial_resolution] == column]['outbreaks'])            
                # convert 'None' str value into int 1
                for idx, val in enumerate(outbreaks):
                    try:
                        outbreaks[idx] = int(val)
                    except ValueError:
                        outbreaks[idx] = 1                
                df.loc[time_point][column] = outbreaks.sum()

        else:  # count by number of rows
            targets = rows.groupby([spatial_resolution]).size().to_frame().T                        
            for col in targets.columns:            
                df.loc[time_point][col] = targets.loc[0][col]
    
        
    df.fillna(0, inplace=True) 
    print(f'Preprocessed data statistics:\n{df.describe()}\n')

    # 4. Write dataframe to csv
    df.to_csv(file_out, sep='\t')

        
def verify(file_in, target_disease, time_range):
    
    df = csv_to_pd(file_in)
    df = df[df.index > time_range]

    for col in df.columns:
        plot(title=f'{target_disease}_{col}', xlabel='timestamp', ylabel='number of outbreaks', x=df.index, y=df[col], save_path=f'{target_disease}_{col}.png')

    plot(title=f'{target_disease}_altogether', xlabel='timestamp', ylabel='number of outbreaks', x=df.index, y=df[:], save_path=f'{target_disease}_altogether.png')
    plot(title=f'{target_disease}_sum', xlabel='timestamp', ylabel='number of outbreaks', x=df.index, y=df[:].sum(axis=1), save_path=f'{target_disease}_sum.png')


def build_trainval(file_in, train_dir, val_dir, time_range, split_ratio):
    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    if not os.path.exists(val_dir):
        os.makedirs(val_dir)

    df = csv_to_pd(file_in)
    df = df[df.index > time_range]
    
    val_data_size = int(len(df) * split_ratio)
    train_df = df[:-val_data_size]
    val_df = df[-val_data_size:]    

    train_df.to_csv(os.path.join(train_dir, 'train.csv'), sep='\t')
    val_df.to_csv(os.path.join(val_dir, 'val.csv'), sep='\t')

    print(f'train data statistics:\n{train_df.describe()}\n')
    print(f'validation data statistics:\n{val_df.describe()}\n')

    
def csv_to_pd(data_path):
    
    df = pd.read_csv(data_path, sep='\t')    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)    
    
    return df  


if __name__ == '__main__':    
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_data', type=str, help='path to OIE csv data')
    parser.add_argument('--preprocessed_data', type=str, help='path to preprocessed data')    
    parser.add_argument('--target_disease', type=str, help='target disease to train & predict')
    parser.add_argument('--spatial_resolution', type=str, help='spatial resolution: country or region')
    parser.add_argument('--target_location', type=str, help='target location to train & predict. Separate by comma. ex) 대한민국,중국,러시아')
    parser.add_argument('--count_by_outbreaks', action='store_true', help='If true, count by number of outbreaks. If false, count by number of rows')
    parser.add_argument('--time_range', type=str, default='2017-01-01', help='time range to look up (start time)')
    parser.add_argument('--build_dataset', action='store_true', help='build train/val csv from preprocessed data')
    parser.add_argument('--split_ratio', type=float, default=0.2, help='split ratio between train data and test data')    
    parser.add_argument('--train_dir', type=str, default='data/train', help='path to train data directory')
    parser.add_argument('--val_dir', type=str, default='data/val', help='path to validation data directory')
    opt = parser.parse_args()

    preprocess(opt.raw_data, opt.preprocessed_data, opt.target_disease, opt.spatial_resolution, opt.target_location, opt.count_by_outbreaks)    
    verify(opt.preprocessed_data, opt.target_disease, opt.time_range)

    if opt.build_dataset:
        build_trainval(opt.preprocessed_data, opt.train_dir, opt.val_dir, opt.time_range, opt.split_ratio)