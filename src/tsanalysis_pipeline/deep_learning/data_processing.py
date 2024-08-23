import torch
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd

class TimeSeriesDataProcessor:
    def __init__(self, df, train_ratio=0.8, window_size=12):
        self.df = df
        self.train_ratio = train_ratio
        self.window_size = window_size
        self.scaler = MinMaxScaler(feature_range=(-1, 1))

    def preprocess(self):
        split_index = int(len(self.df) * self.train_ratio)
        train_df = self.df[:split_index]
        test_df = self.df[split_index:]
        
        train_norm = self.scaler.fit_transform(train_df)
        test_norm = self.scaler.transform(test_df)
        
        train_norm = torch.FloatTensor(train_norm).view(-1)
        test_norm = torch.FloatTensor(test_norm).view(-1)
        
        train_data = self.create_sequences(train_norm)
        test_data = self.create_sequences(test_norm)
        
        return train_data, test_data, test_norm

    def create_sequences(self, data):
        sequences = []
        for i in range(len(data) - self.window_size):
            seq = data[i:i+self.window_size]
            label = data[i+self.window_size:i+self.window_size+1]
            sequences.append((seq, label))
        return sequences

    def inverse_transform(self, data):
        return self.scaler.inverse_transform(np.array(data).reshape(-1, 1))
