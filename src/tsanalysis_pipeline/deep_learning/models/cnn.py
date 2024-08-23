import torch
import torch.nn as nn

class CNNTimeSeriesModel(nn.Module):
    def __init__(self, input_size, hidden_size=64, output_size=1):
        super(CNNTimeSeriesModel, self).__init__()
        self.conv1d = nn.Conv1d(1, hidden_size, kernel_size=2)
        self.relu = nn.ReLU(inplace=True)
        self.fc1 = nn.Linear(hidden_size * (input_size - 1), 50)
        self.fc2 = nn.Linear(50, output_size)

    def forward(self, x):
        x = self.conv1d(x)
        x = self.relu(x)
        x = x.view(x.size(0), -1)
        x = self.fc1(x)
        x = self.fc2(x)
        return x
