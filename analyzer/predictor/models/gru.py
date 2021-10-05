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
        x = x.transpose(0, 1)  # (batch_size, window_size, n_features) -> (window_size, batch_size, n_features)  ex) (10, 1, 4)
        self.gru.flatten_parameters()
        outs, _ = self.gru(x)  # outs.shape = (window_size, batch_size, n_hidden * 2)  ex) (10, 1, 256)
        out = self.fc(outs[-1])  # out.shape = (batch_size, n_features)  ex) (1, 256) x (256, 4) = (1, 4)
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
        x = x.transpose(0, 1)
        self.gru.flatten_parameters()
        outs, _ = self.gru(x)        
        out = self.fc(outs[-1])        
        return out