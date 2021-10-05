import torch
import torch.nn as nn


class LSTMPredictor(nn.Module):
    
    def __init__(self, device, n_features=1, n_hidden=512, n_layers=2, window_size=10):
        super(LSTMPredictor, self).__init__()

        self.device = device
        self.n_hidden = n_hidden
        self.n_layers = n_layers
        self.window_size = window_size
    
        self.hidden_states = torch.zeros(self.n_layers, self.window_size, self.n_hidden).to(self.device)
        self.cell_states = torch.zeros(self.n_layers, self.window_size, self.n_hidden).to(self.device)

        self.lstm = nn.LSTM(input_size=n_features, hidden_size=n_hidden, num_layers=n_layers, dropout=0.5)        
        self.linear = nn.Linear(in_features=n_hidden, out_features=1)        
        self.activation = nn.ReLU()        
                          

    def reset_states(self):
        self.hidden_states = torch.zeros(self.n_layers, self.window_size, self.n_hidden).to(self.device)
        # self.hidden_states = torch.zero_(self.n_layers, self.window_size, self.n_hidden).to(self.device)
        self.cell_states = torch.zeros(self.n_layers, self.window_size, self.n_hidden).to(self.device)


    # Given data_len=1341, window_size=10, n_hidden=512,
    # sequences.shape = ((data_len - window_size - 1), window_size, 1)  ex) (1341, 10, 1)
    def forward(self, sequences):
        # sequences.view(len(sequences), window_size, -1).shape = (1341, 10, 1)
        # lstm_out.shape = (1341, 10, 512), hidden_states.shape = (10, 512), cell_states[0].shape = (10, 512)        
        lstm_out, (self.hidden_states, self.cell_states) = self.lstm(sequences.view(len(sequences), self.window_size, -1), (self.hidden_states, self.cell_states))
        # lstm_out.view(self.window_size, len(sequences), self.n_hidden).shape = (10, 1341, 512)
        # last_time_step.shape = (1341, 512)
        last_time_step = lstm_out.view(self.window_size, len(sequences), self.n_hidden)[-1]     
        # y_pred.shape(1341, 1)
        y_pred = self.activation(self.linear(last_time_step))

        return y_pred
        