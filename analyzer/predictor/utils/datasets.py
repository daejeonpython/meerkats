import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt


def create_dataloader(data_path, split_ratio=0.2, seq_len=10):

    df = csv_to_pd(data_path)
    data = np.array(df["outbreaks"])
    test_data_size = int(len(data) * split_ratio)
        
    print(f'Validation data size: {test_data_size}')

    train_data = data[:-test_data_size]
    test_data = data[-test_data_size:]
    print(len(train_data))
    print(len(test_data))

    train_dataset = OIEDataset(train_data, seq_len)
    test_dataset = OIEDataset(test_data, seq_len)

    # train_loader = DataLoader(train_dataset)
    # test_loader = DataLoader(test_dataset)
 
    # return train_loader, test_loader
    return df, train_data, test_data, train_dataset, test_dataset


class OIEDataset(Dataset):
    
    def __init__ (self, data, seq_len):                
                        
        self.scaler = MinMaxScaler()
        self.scaler = self.scaler.fit(np.expand_dims(data, axis=1))
        self.data = self.scaler.transform(np.expand_dims(data, axis=1))                
        self.x, self.y = create_sequences(self.data, seq_len)        

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        # return self.x[index], self.y[index]
        return self.x, self.y


def csv_to_pd(data_path):
    
    df = pd.read_csv(data_path, sep='\t')    
    df["date"] = pd.to_datetime(df["date"])    
    # df.drop(df.loc[df["date"] < '2017-01-01'].index, inplace=True)
    df.set_index("date", inplace=True)    
    print(df.head)
    print(df.shape)
    print(df.dtypes)

    # plt.figure(figsize=(12, 8))
    # plt.plot(df["outbreaks"])
    # plt.show()
        
    return df


def create_sequences(data, seq_len):
    xs = []
    ys = []

    for i in range(len(data) - seq_len - 1):
        x = data[i:(i + seq_len)]
        y = data[i + seq_len]
        xs.append(x)
        ys.append(y)
    
    return np.array(xs), np.array(ys)


