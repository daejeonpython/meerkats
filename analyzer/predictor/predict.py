import argparse
import easydict
import numpy as np
import pandas as pd

import torch
from utils.preprocessor import csv_to_pd
from utils.plots import plot_inference_result
from models.transformer import transformer


def predict(opt):
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'    

    with open(opt.weight, 'rb') as f:
        saved_model = torch.load(f)
    scaler = saved_model['scaler']
    window_size = saved_model['window_size']
    ahead = saved_model['ahead']
    print(f"best epoch: {saved_model['best_epoch']}")
    print(f"window_size: {window_size}")
    print(f'ahead: {ahead}')

    observed_df = csv_to_pd(opt.test_data)    
    last_window_days = observed_df[-window_size:]   

    model_args = easydict.EasyDict({
        'output_size': saved_model['output_size'],
        'window_size': window_size,
        'ahead': ahead,
        'batch_size': opt.batch_size,        
        'e_features': saved_model['e_features'],
        'd_features': saved_model['d_features'],
        'd_hidn': saved_model['d_hidn'],
        'n_head': saved_model['n_head'],
        'd_head': saved_model['d_head'],
        'dropout': saved_model['dropout'],
        'd_ff': saved_model['d_ff'],
        'n_layer': saved_model['n_layer'],
        'dense_h': saved_model['dense_h'],        
        'device': device
    })

    model = transformer(model_args).to(device)
    model.load_state_dict(saved_model['state'])    
    model.eval()    

    with torch.no_grad():
        x = last_window_days.to_numpy().reshape(-1)        
        x = scaler.transform(np.expand_dims(x, axis=1))
        x = x.reshape(-1, observed_df.shape[-1])        
        x = torch.from_numpy(x).float().unsqueeze(0)
        y_pred = model(x.to(device), x.to(device))   # y_pred.shape = (batch_size, ahead. n_features)  ex) (1, 2, 4)            
        y_pred = y_pred.cpu().numpy()        
      
    for idx, col in enumerate(observed_df.columns):                
        future = pd.date_range(observed_df.index[-1], periods=ahead + 1)
        predicted_cases = scaler.inverse_transform(y_pred[:, :, idx]).flatten()
        predicted_cases = np.append(observed_df[col][-1], predicted_cases)        
        plot_inference_result(observed_df, col, future, predicted_cases)          
        

if __name__ == '__main__':    
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_data', type=str, help='path to the test data')    
    parser.add_argument('--batch_size', type=int)
    parser.add_argument('--weight', type=str, help='path to the weight file')    
    opt = parser.parse_args()
    
    predict(opt)