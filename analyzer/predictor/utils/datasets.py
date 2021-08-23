import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt


def create_dataset(data_path, split_ratio=0.2, seq_len=10):

    df = csv_to_pd(data_path)
    data = np.array(df["outbreaks"])
    test_data_size = int(len(data) * split_ratio)
        
    train_data = data[:-test_data_size]
    test_data = data[-test_data_size:]
    print(f'train data size: {len(train_data)}')
    print(f'test data size: {len(test_data)}')

    scaler = MinMaxScaler()
    # ehong 210823: Should I fit scaler into total data? or train data first then test data?
    scaler = scaler.fit(np.expand_dims(train_data, axis=1))  # np.expand_dims(data, axis=1).shape = (data_len, 1)
    train_data = scaler.transform(np.expand_dims(train_data, axis=1))  # normalize data between 0 and 1
    test_data = scaler.transform(np.expand_dims(test_data, axis=1))
 
    train_points, train_labels = create_sequences(train_data, seq_len)
    test_points, test_labels = create_sequences(test_data, seq_len)

    return df, scaler, train_data, test_data, train_points, train_labels, test_points, test_labels


# Leave this for now
'''
class OIEDataset(Dataset):
    
    def __init__ (self, data, seq_len):                
                        
        self.scaler = MinMaxScaler()
        self.scaler = self.scaler.fit(np.expand_dims(data, axis=1))  # np.expand_dims(data, axis=1).shape = (data_len, 1)
        self.data = self.scaler.transform(np.expand_dims(data, axis=1))  # normalize data between 0 and 1
        self.x, self.y = create_sequences(self.data, seq_len)        

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        # return self.x[index], self.y[index]
        return self.x, self.y
'''


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
    
    # np.array(xs).shape = ((data_len - seq_len - 1), seq_len, 1)  ex) (1341, 10, 1)
    # np.array(ys).shape = ((data_len - seq_len - 1), 1)  ex) (1341, 1)
    # For each sequence of "seq_len" data points 
    return np.array(xs), np.array(ys)


