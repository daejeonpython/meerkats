import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import matplotlib.pyplot as plt


def create_dataloader(data_path, batch_size, split_ratio=0.2, seq_len=10):
    
    df = csv_to_pd(data_path)
    data = np.array(df['outbreaks'])
    test_data_size = int(len(data) * split_ratio)

    train_data = data[:-test_data_size]
    test_data = data[-test_data_size:]
    train_data = torch.from_numpy(train_data).float()
    test_data = torch.from_numpy(test_data).float()
    print(f'train data size: {len(train_data)}')
    print(f'test data size: {len(test_data)}')
    
    scaler = MinMaxScaler()
    scaler = scaler.fit(np.expand_dims(train_data, axis=1))  # np.expand_dims(data, axis=1).shape = (data_len, 1)
    train_data = scaler.transform(np.expand_dims(train_data, axis=1))  # normalize data between 0 and 1
    test_data = scaler.transform(np.expand_dims(test_data, axis=1))

    train_dataset = OIEDataset(train_data, seq_len)
    test_dataset = OIEDataset(test_data, seq_len)

    train_loader = DataLoader(train_dataset, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    
    return df, scaler, train_loader, test_loader


class OIEDataset(Dataset):
    
    def __init__ (self, data, seq_len):                
        
        self.data = data
        self.seq_len = seq_len
        self.x, self.y = create_sequences(self.data, self.seq_len)

    def __len__(self):
        return len(self.x)

    def __getitem__(self, index):
        return self.x[index], self.y[index]
        

def csv_to_pd(data_path):
    
    df = pd.read_csv(data_path, sep='\t')    
    df['date'] = pd.to_datetime(df['date'])    
    # df.drop(df.loc[df['date'] < '2017-01-01'].index, inplace=True)
    df.set_index('date', inplace=True)    
        
    return df


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


