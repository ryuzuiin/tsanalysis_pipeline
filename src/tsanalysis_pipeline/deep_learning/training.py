import torch
import torch.nn as nn
import torch.optim as optim
import time

class TimeSeriesTrainer:
    def __init__(self, model, train_data, learning_rate=0.001, epochs=100):
        self.model = model
        self.train_data = train_data
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        self.epochs = epochs
        self.train_losses = []

    def train(self):
        self.model.train()
        start_time = time.time()
        for epoch in range(self.epochs):
            epoch_loss = 0
            for seq, label in self.train_data:
                self.optimizer.zero_grad()
                y_pred = self.model(seq.unsqueeze(0).unsqueeze(0))
                loss = self.criterion(y_pred, label)
                loss.backward()
                self.optimizer.step()
                epoch_loss += loss.item()
            
            avg_loss = epoch_loss / len(self.train_data)
            self.train_losses.append(avg_loss)
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch: {epoch+1:03d}/{self.epochs:03d} | Loss: {avg_loss:.8f}')
        
        print(f'\nTraining Duration: {time.time() - start_time:.0f} seconds')

    def get_train_losses(self):
        return self.train_losses