import torch
import torch.nn


class BidirectionalGRU(torch.nn.Module):
    def __init__(self, n_features=1, n_hidden=128, n_layers=3):
        super().__init__()
        self.gru = torch.nn.GRU(
            input_size=n_features,
            hidden_size=n_hidden,
            num_layers=n_layers,
            bidirectional=True,
            dropout=0,
        )
        self.fc = torch.nn.Linear(n_hidden * 2, n_features)        
    
    def forward(self, x):
        x = x.transpose(0, 1)  # (batch, seq, params) -> (seq, batch, params)
        self.gru.flatten_parameters()
        outs, _ = self.gru(x)        
        out = self.fc(outs[-1])        
        return out


class UnidirectionalGRU(torch.nn.Module):
    def __init__(self, n_features=1, n_hidden=128, n_layers=3):
        super().__init__()
        self.gru = torch.nn.GRU(
            input_size=n_features,
            hidden_size=n_hidden,
            num_layers=n_layers,
            bidirectional=False,
            dropout=0,
        )
        self.fc = torch.nn.Linear(n_hidden, n_features)        
    
    def forward(self, x):
        x = x.transpose(0, 1)  # (batch, seq, params) -> (seq, batch, params)
        self.gru.flatten_parameters()
        outs, _ = self.gru(x)        
        out = self.fc(outs[-1])        
        return out