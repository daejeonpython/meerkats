import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from utils.preprocessor import csv_to_pd


def create_dataloader(data_path, is_train, scaler, batch_size, seq_len=10, ahead=1):
    
    df = csv_to_pd(data_path)    
    print(f'df.shape: {df.shape}')    
    print(df.describe())
    outbreaks = np.array(df[:])    
    
    if is_train:        
        outbreaks = outbreaks.reshape(-1)  # reshape 2d matrix to 1d vector for MinMaxScaler().transform
        
        scaler = MinMaxScaler()
        scaler = scaler.fit(np.expand_dims(outbreaks, axis=1))  # np.expand_dims(data, axis=1).shape = (data_len, 1)
        scaled_outbreaks = scaler.transform(np.expand_dims(outbreaks, axis=1))  # normalize data between 0 and 1            
        scaled_outbreaks = scaled_outbreaks.reshape(-1, df.shape[-1])  # reshape 1d vector back to 2d matrix        
        print(f'boundary_check: {boundary_check(scaled_outbreaks)}')
        scaled_outbreaks = torch.from_numpy(scaled_outbreaks).float() # numpy default float64 -> torch default float32
        
        dataset = OIEDataset(scaled_outbreaks, seq_len)            
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        return df, dataloader, scaler
        
    else:            
        outbreaks = outbreaks.reshape(-1)
        
        scaled_outbreaks = scaler.transform(np.expand_dims(outbreaks, axis=1))
        scaled_outbreaks = scaled_outbreaks.reshape(-1, df.shape[-1])       
        print(f'boundary_check: {boundary_check(scaled_outbreaks)}')
        scaled_outbreaks = torch.from_numpy(scaled_outbreaks).float() # numpy default float64 -> torch default float32
        
        dataset = OIEDataset(scaled_outbreaks, seq_len)  
        dataloader = DataLoader(dataset, batch_size=batch_size)
        return df, dataloader


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
    
    # torch.stack(xs).shape = ((data_len - seq_len - 1), seq_len, n_features)  ex) (1341, 10, 4)
    # torch.stack(ys).shape = ((data_len - seq_len - 1), n_features)  ex) (1341, 4)
    # For each sequence of 'seq_len' data points 
    return torch.stack(xs), torch.stack(ys)


