import torch
import torch.nn as nn
import torch.nn.functional as F


class TagPredictor(nn.Module):
    def __init__(self, input_size=1000, hidden_size=512, num_tags=100, dropout_rate=0.5):
        super(TagPredictor, self).__init__()
        self.num_tags = num_tags
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.in1 = nn.InstanceNorm1d(hidden_size)
        self.dropout1 = nn.Dropout(dropout_rate)
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.in2 = nn.InstanceNorm1d(hidden_size // 2)
        self.dropout2 = nn.Dropout(dropout_rate)
        self.fc3 = nn.Linear(hidden_size // 2, num_tags)
        self.in3 = nn.InstanceNorm1d(num_tags)

    def forward(self, x):
        x = F.relu(self.in1(self.fc1(x)))
        x = self.dropout1(x)
        x = F.relu(self.in2(self.fc2(x)))
        x = self.dropout2(x)
        x = torch.sigmoid(self.in3(self.fc3(x)))
        return x

    def update_output_layer(self, new_num_tags):
        self.fc3 = nn.Linear(self.fc2.out_features, new_num_tags)
        self.in3 = nn.InstanceNorm1d(new_num_tags)
        self.num_tags = new_num_tags

    def predict_tags(self, features):
        self.eval()
        with torch.no_grad():
            predictions = self.forward(features)
            high_confidence_tags = (predictions > 0.65).nonzero(as_tuple=True)[1]
            return high_confidence_tags.tolist()
