import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import math

class TimeSeriesEvaluator:
    def __init__(self, model, data_processor, test_norm, window_size):
        self.model = model
        self.data_processor = data_processor
        self.test_norm = test_norm
        self.window_size = window_size

    def predict(self):
        self.model.eval()
        predictions = []
        
        with torch.no_grad():
            current_sequence = self.test_norm[:self.window_size]
            for _ in range(len(self.test_norm) - self.window_size):
                input_seq = current_sequence.unsqueeze(0).unsqueeze(0)
                output = self.model(input_seq)
                predictions.append(output.item())
                current_sequence = torch.cat((current_sequence[1:], output.view(-1)))

        true_predictions = self.data_processor.inverse_transform(predictions)
        return true_predictions

    def calculate_metrics(self, true_values, predictions):
        mse = mean_squared_error(true_values, predictions)
        rmse = math.sqrt(mse)
        mape = mean_absolute_percentage_error(true_values, predictions) * 100
        return mse, rmse, mape

    def plot_results(self, true_values, predictions, train_losses):
        plt.figure(figsize=(15, 10))
        
        # Training Loss
        plt.subplot(3, 1, 1)
        plt.plot(train_losses)
        plt.title('Training Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        
        # Predictions vs Actual
        plt.subplot(3, 1, 2)
        plt.plot(true_values.index, true_values.values, label='Actual')
        plt.plot(true_values.index, predictions, label='Prediction')
        plt.title('Predictions vs Actual')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend()
        
        # Absolute Error
        plt.subplot(3, 1, 3)
        plt.plot(true_values.index, np.abs(true_values.values - predictions), label='Absolute Error')
        plt.title('Prediction Error')
        plt.xlabel('Time')
        plt.ylabel('Absolute Error')
        plt.legend()
        
        plt.tight_layout()
        plt.show()