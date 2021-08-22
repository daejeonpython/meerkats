import torch
import torch.nn as nn


class LSTMPredictor(nn.Module):
    def __init__(self, n_features, n_hidden, seq_len, n_layers, device):
        super(LSTMPredictor, self).__init__()

        self.n_hidden = n_hidden
        self.seq_len = seq_len
        self.n_layers = n_layers
        self.device = device

        self.hidden_states = torch.zeros(self.n_layers, self.seq_len, self.n_hidden).to(self.device)
        self.cell_states = torch.zeros(self.n_layers, self.seq_len, self.n_hidden).to(self.device)

        self.lstm = nn.LSTM(input_size=n_features, hidden_size=n_hidden, num_layers=n_layers, dropout=0.3)
        self.linear = nn.Linear(in_features=n_hidden, out_features=1)
        self.activation = nn.ReLU()

        '''
        for name, param in self.named_parameters():
            torch.nn.init.normal_(param)            
        '''

    def reset_states(self):
        self.hidden_states = torch.zeros(self.n_layers, self.seq_len, self.n_hidden).to(self.device)
        self.cell_states = torch.zeros(self.n_layers, self.seq_len, self.n_hidden).to(self.device)


    # sequences.shape = (1341, 10, 1) (sentence length, window_size, number of features))
    def forward(self, sequences): 
        # lstm_out.shape = (1341, 10, 512), hidden_states.shape = (10, 512), cell_states[0].shape = (10, 512)
        # sequences.view(len(sequences), self.seq_len, -1).shape = (1341, 10, 1)
        lstm_out, (self.hidden_states, self.cell_states) = self.lstm(sequences.view(len(sequences), self.seq_len, -1), (self.hidden_states, self.cell_states))
        # last_time_step.shape = (1341, 512)
        last_time_step = lstm_out.view(self.seq_len, len(sequences), self.n_hidden)[-1]     
        # y_pred.shape(1341, 1)             
        y_pred = self.activation(self.linear(last_time_step))

        return y_pred
        