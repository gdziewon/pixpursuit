"""
services/tag_prediction/tag_predictor.py

This module defines the TagPredictor class, a neural network model for predicting tags based on image features.
It uses a sequence of linear layers with Instance Normalization and Dropout to generate predictions.
"""


import torch
import torch.nn as nn
import torch.nn.functional as F
from utils.constants import TAG_PREDICTION_THRESHOLD


class TagPredictor(nn.Module):
    """
    A neural network for predicting tags based on image features.

    This model uses a series of fully connected layers with Instance Normalization and Dropout for regularization.

    Attributes:
        num_tags (int): The number of unique tags to predict.
        fc1 (nn.Linear): First fully connected layer.
        in1 (nn.InstanceNorm1d): Instance normalization layer after the first fully connected layer.
        dropout1 (nn.Dropout): Dropout layer after the first instance normalization layer.
        fc2 (nn.Linear): Second fully connected layer.
        in2 (nn.InstanceNorm1d): Instance normalization layer after the second fully connected layer.
        dropout2 (nn.Dropout): Dropout layer after the second instance normalization layer.
        fc3 (nn.Linear): Third fully connected layer that outputs the final prediction scores for each tag.
        in3 (nn.InstanceNorm1d): Instance normalization layer after the third fully connected layer.
    """
    def __init__(self, input_size=1000, hidden_size=512, num_tags=100, dropout_rate=0.5):
        """
        Initializes the TagPredictor model with the given architecture parameters.

        :param input_size: The size of the input feature vector.
        :param hidden_size: The size of the hidden layers.
        :param num_tags: The number of unique tags to predict.
        :param dropout_rate: The dropout rate for regularization.
        """
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
        """
        Defines the forward pass of the model.

        :param x: The input tensor containing features.
        :return: The output tensor containing the predicted tag probabilities.
        """
        x = F.relu(self.in1(self.fc1(x)))
        x = self.dropout1(x)
        x = F.relu(self.in2(self.fc2(x)))
        x = self.dropout2(x)
        x = torch.sigmoid(self.in3(self.fc3(x)))
        return x

    def update_output_layer(self, new_num_tags):
        """
        Updates the output layer of the model to predict a new number of tags.

        :param new_num_tags: The new number of unique tags to predict.
        """
        self.fc3 = nn.Linear(self.fc2.out_features, new_num_tags)
        self.in3 = nn.InstanceNorm1d(new_num_tags)
        self.num_tags = new_num_tags

    def predict_tags(self, features):
        """
        Predicts tags for given features, identifying those with high confidence.

        :param features: The input tensor containing features for prediction.
        :return: A list of indices for tags with high confidence predictions.
        """
        self.eval()
        with torch.no_grad():
            predictions = self.forward(features)
            high_confidence_tags = (predictions > TAG_PREDICTION_THRESHOLD).nonzero(as_tuple=True)[1]
            return high_confidence_tags.tolist()
