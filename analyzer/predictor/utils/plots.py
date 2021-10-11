import os
import matplotlib
import matplotlib.pyplot as plt
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
font = matplotlib.font_manager.FontProperties(fname=font_path).get_name()
matplotlib.rc('font', family=font)

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning) 


def plot(title, xlabel, ylabel, x, y, save_path):
    plt.figure(figsize=(12,8))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.plot(x, y)
    plt.savefig(save_path)


def plot_eval_result(observed_df, test_df, predicted_cases, col, window_size, ahead, show_observed_cases):

    plt.figure(figsize=(12, 8))
    plt.title(f'Prediction Graph in {col}')
    plt.xlabel('timestamp')
    plt.ylabel('number of outbreaks')

    if show_observed_cases:
        plt.plot(observed_df.index, observed_df[col], label='Observed Daily Cases')                
        plt.plot(test_df.index, test_df[col], label='True Cases')        
        plt.plot(test_df.index[(window_size + 1):len(test_df) + 1 - ahead], predicted_cases, label='Predicted Cases')        
        plt.legend()
        plt.savefig(os.path.join('runs', f'{col}_observation+prediction.png'))  
    
    else:
        plt.plot(test_df.index, test_df[col], label='True Cases')        
        plt.plot(test_df.index[(window_size + 1):len(test_df) + 1 - ahead], predicted_cases, label='Predicted Cases')        
        plt.legend()
        plt.savefig(os.path.join('runs', f'{col}_prediction.png'))  


def plot_inference_result(observed_df, col, future, predicted_cases):
    
    plt.figure(figsize=(12, 8))
    plt.title(f'Prediction Graph in {col}')
    plt.xlabel('timestamp')
    plt.ylabel('number of outbreaks')
    
    plt.plot(observed_df.index, observed_df[col], label='Observed Daily Cases')
    plt.plot(future, predicted_cases, label='Predicted Cases')
    plt.plot()
    plt.legend()
    plt.savefig(os.path.join('runs', f'{col}_prediction.png'))

