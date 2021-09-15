import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def create_dataloader(data_path, is_train, scaler, batch_size, split_ratio=0.2, seq_len=10):
    
    df = csv_to_pd(data_path)    
    print(f'df.shape: {df.shape}')
    
    test_data_size = int(len(df) * split_ratio)
    outbreaks = np.array(df['outbreaks'])
    
    if is_train:
        outbreaks = outbreaks[:-test_data_size]
        outbreaks = torch.from_numpy(outbreaks).float() # numpy default float64 -> torch default float32
        print(f'len(outbreaks): {len(outbreaks)}')
        scaler = MinMaxScaler()
        scaler = scaler.fit(np.expand_dims(outbreaks, axis=1))  # np.expand_dims(data, axis=1).shape = (data_len, 1)
        scaled_outbreaks = scaler.transform(np.expand_dims(outbreaks, axis=1))  # normalize data between 0 and 1    
        print(f'boundary_check: {boundary_check(scaled_outbreaks)}')
        
        dataset = OIEDataset(scaled_outbreaks, seq_len)            
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        return df, dataloader, scaler
        
    else:
        outbreaks = outbreaks[-test_data_size:]
        outbreaks = torch.from_numpy(outbreaks).float()
        scaled_outbreaks = scaler.transform(np.expand_dims(outbreaks, axis=1))
        print(f'boundary_check: {boundary_check(scaled_outbreaks)}')
        
        dataset = OIEDataset(scaled_outbreaks, seq_len)  
        dataloader = DataLoader(dataset, batch_size=batch_size)
        return df, dataloader


def csv_to_pd(data_path):
    
    df = pd.read_csv(data_path, sep='\t')    
    df['date'] = pd.to_datetime(df['date'])    
    # df.drop(df.loc[df['date'] < '2017-01-01'].index, inplace=True)
    df.set_index('date', inplace=True)    

    return df     


def boundary_check(x):    
    return np.any(x > 1.0), np.any(x < 0), np.any(np.isnan(x))


class OIEDataset(Dataset):
    
    def __init__ (self, data, seq_len):                
        
        self.data = data
        self.seq_len = seq_len
        self.x, self.y = create_sequences(self.data, self.seq_len)

    def __len__(self):
        return len(self.x)

    def __getitem__(self, index):
        return self.x[index], self.y[index]
        

def create_sequences(data, seq_len):
    xs = []
    ys = []

    for i in range(len(data) - seq_len - 1):
        x = data[i:(i + seq_len)]
        y = data[i + seq_len]
        xs.append(x)
        ys.append(y)
    
    # np.array(xs).shape = ((data_len - seq_len - 1), seq_len, 1)  ex) (1341, 10, 1)
    # np.array(ys).shape = ((data_len - seq_len - 1), 1)  ex) (1341, 1)
    # For each sequence of 'seq_len' data points 
    return np.array(xs), np.array(ys)


