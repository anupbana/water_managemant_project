# DummyData.py
import pandas as pd
import random
from datetime import datetime, timedelta

def SampleData(house_number):
    # THIS CODE WRITES DATA ONLY FOR 3 HOUSES AT A TIME
    columns = ['HouseNO', 'Quantity', 'FromTime', 'ToTime', 'Date']# column names
    house_numbers = house_number# only three houses at a time
    num_entries = 10047# number of entries per house

    # Define start date, time, and interval
    start_date = datetime(2024, 4, 1)  # Define your start date here
    start_time = datetime(2024, 4, 1, 0, 0)  # Define your start time here
    interval = timedelta(hours=1)  # Define your interval here (1 hour in this case)

    df = pd.DataFrame(columns=columns)

    # 1. Write the house numbers 
    house_list = []
    for i in range(num_entries):
        house_list.append(house_numbers[0])
        house_list.append(house_numbers[1])
        house_list.append(house_numbers[2])
    df['HouseNO'] = house_list

    # 2. Write random consumption quantities
    quantity_list = []
    for i in range(num_entries*3):
        quantity_list.append(random.randrange(0, 45))# in rangle 0-45 lt
    df['Quantity'] = quantity_list

    # 3.Generate timestamps in hourly intervals
    timestamps = []
    current_date = start_date
    current_time = start_time
    for _ in range(num_entries): 
        timestamps.append((current_date.strftime('%Y-%m-%d'), current_time.strftime('%H:%M:%S'), (current_time + interval).strftime('%H:%M:%S')))
        current_time += interval
        if current_time.hour == 0:  # Increment date after every 24 hours
            current_date += timedelta(days=1)
    # Store the final output in a list
    output_list = []
    for index, (date, from_time, to_time) in enumerate(timestamps):
        output_list.append({"Entry": index+1, "Date": date, "FromTime": from_time, "ToTime": to_time})
    # Do the preprocessing to append to the data frame 
    final_from_time = []
    final_to_time = []
    final_date = []
    for i in range(len(df)//3):
        final_from_time.append(output_list[i]['FromTime'])
        final_from_time.append(output_list[i]['FromTime'])
        final_from_time.append(output_list[i]['FromTime'])

        final_to_time.append(output_list[i]['ToTime'])
        final_to_time.append(output_list[i]['ToTime'])
        final_to_time.append(output_list[i]['ToTime'])

        final_date.append(output_list[i]['Date'])
        final_date.append(output_list[i]['Date'])
        final_date.append(output_list[i]['Date'])

    df['FromTime'] = final_from_time
    df['ToTime'] = final_to_time
    df['Date'] = final_date

    return(df)
    
