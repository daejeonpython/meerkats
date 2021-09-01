import os
import datetime
from datetime import timedelta
import pandas as pd
import matplotlib.pyplot as plt


def get_time_series(start, end):
    time_series = []
    delta = end - start
    for i in range(delta.days + 1):
        day = start + timedelta(days=i)
        time_series.append(day)
    return time_series


def read_lines(file_path):
    list_of_lines = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.endswith("\n"):
                line = line.rstrip("\n")
            list_of_lines.append(line)
    return list_of_lines


def preprocess(file_in, file_out):
    
    # 1. Read the raw file
    lines = read_lines(file_in)
    data = dict()
    for idx, line in enumerate(lines):
        if idx == 0:
            continue
        tokens = line.split("\t")
        try:
            data[datetime.datetime.strptime(tokens[0], "%Y-%m-%d").date()].append(dict(disease=tokens[1], serotype=tokens[2], species=tokens[3], country=tokens[6], outbreaks=tokens[5]))            
        except KeyError:
            data[datetime.datetime.strptime(tokens[0], "%Y-%m-%d").date()] = [dict(disease=tokens[1], serotype=tokens[2], species=tokens[3], country=tokens[6], outbreaks=tokens[5])]
                
    
    sorted_by_date = sorted(data.items(), key=lambda x: x[0], reverse=False)
    
    # Since OIE data suffer from data sparsity before 2017, we start from 2017    
    first_date = datetime.datetime.strptime("2017-01-01", "%Y-%m-%d").date()
    # first_date = sorted_by_date[0][0]
    last_date = sorted_by_date[-1][0]
    print(f'First_date: {first_date}')
    print(f'Last_date: {last_date}')
    
    # 2. Get time range between the first date and the last date
    time_series = get_time_series(first_date, last_date)

    # 3. Write the preprocessed data with respect to date
    with open(file_out, "w", encoding="utf-8") as f:
        for time in time_series:
            if time in data:
                events = data[time]
                for event in events:
                    f.write(
                        f'{time}\t{event["disease"]}\t{event["serotype"]}\t{event["species"]}\t{event["country"]}\t{event["outbreaks"]}\n')
            else:
                f.write(f'{time}\tn/a\tn/a\tn/a\tn/a\tn/a\tn/a\n')


def distill(file_in, file_out, target_disease, row_count=True):
    
    data = dict()
    lines = read_lines(file_in)
    
    for line in lines:
        columns = line.split("\t")
        date, disease, outbreaks = columns[0], columns[1], columns[5]
        if disease == target_disease: 
            if row_count:     
                try:
                    data[date] += 1
                except KeyError:
                    data[date] = 1
            else:
                try:
                    if outbreaks != "None":
                        data[date] += int(outbreaks)
                    else:
                        data[date] += 1
                except KeyError:
                    if outbreaks != "None":
                        data[date] = int(outbreaks)
                    else:
                        data[date] = 1
        else:
            if date not in data:
                data[date] = 0

    with open(file_out, "w", encoding="utf-8") as f:
        f.write("date\toutbreaks\n")
        for key in data:
            f.write(f'{key}\t{data[key]}\n')


def verify(file_in):
    df = pd.read_csv(file_in, sep="\t")
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    plt.figure(figsize=(12, 8))
    plt.plot(df["outbreaks"])
    plt.savefig(os.path.join("..", "data", "plot.png"))


if __name__ == "__main__":
    raw_data = os.path.join("..", "data", "data.csv")
    preprocessed_data = os.path.join("..", "data", "preprocessed_data.csv")
    target_disease = "아프리카돼지열병"
    distilled_data = os.path.join("..", "data", "distilled_data.csv")

    preprocess(raw_data, preprocessed_data)
    distill(preprocessed_data, distilled_data, target_disease)
    verify(distilled_data)