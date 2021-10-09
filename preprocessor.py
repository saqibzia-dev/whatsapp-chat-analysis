import pandas as pd
import re
import streamlit as st
@st.cache(suppress_st_warning=True)
def preprocess(data):
    pattern = '\d{1,2}\/\d{1,2}\/\d{2,4},\s\d{1,2}:\d{1,2}\s?\w[pm|am]?\s-\s'
    pattern_datetime = '\d{1,2}\/\d{1,2}\/\d{2,4},\s\d{1,2}:\d{1,2}\s?\w[pm|am]?'
    am_pm_check = '\d{1,2}\/\d{1,2}\/\d{2,4},\s\d{1,2}:\d{1,2}\s?\w[pm|am]'

    #getting all the messages
    messages = re.split(pattern,data)[1:]

    #getting all the date-time when the messages are sent
    dates = re.findall(pattern_datetime,data)

    # checking which format time is
    date_check = '18/09/2018, 15:02'
    time_format = 24
    time_matches = re.findall(am_pm_check,data)
    #print(time_matches)
    if time_matches:
        #print("12 hr format")
        time_format = 12
    #else:
    #   print("24 hr format")

    # converting data into pandas dataframe
    df = pd.DataFrame({"user_messages":messages,"date_time":dates})

    # converting date into proper datetime format
    if time_format == 12:
       # df["date_time"] = pd.to_datetime(df["date_time"],format = "%d/%m/%Y, %I:%M %p")
        df["date_time"] = pd.to_datetime(df["date_time"])
    else:
        df["date_time"] = pd.to_datetime(df["date_time"])
        #df["date_time"] = pd.to_datetime(df["date_time"],format = "%d/%m/%Y, %H:%M")
    df.rename(columns = {"date_time":"date_sent"} ,inplace = True)

        #separate users and messages
    users =  []
    messages = []
    for message in df['user_messages']:
        splitted_message = message.split(':')
        #print(splitted_message)
        #print(len(splitted_message))
        if len(splitted_message) == 1:
            users.append("group_notification")
            messages.append(splitted_message[0])
        else:
            users.append(splitted_message[0])
            #messages.append(splitted_message[1:])
            #to avoid creating an array we join the list with " "
            message_without_list = "".join(splitted_message[1:])
            messages.append(message_without_list)

    df['user'] = users
    df['message'] = messages
    df.drop(columns = ["user_messages"],inplace = True)
    #extracting day,month,year,hours,minutes
    df['year'] = df['date_sent'].dt.year
    df['month'] = df['date_sent'].dt.month_name()
    df['month_num'] = df['date_sent'].dt.month
    df['only_date'] = df['date_sent'].dt.date
    df['day'] = df['date_sent'].dt.day
    df['day_name'] = df['date_sent'].dt.day_name()
    df['hour'] = df['date_sent'].dt.hour
    df['minute'] = df['date_sent'].dt.minute
    period = []
    for hour in df[['hour','minute']]['hour']:
        #print(hour)
        if hour == 23:
            period.append(str(hour)+"-"+str("00"))
        elif hour==0:
            period.append(str('00')+"-"+str(hour+1))
        else:
            period.append(str(hour)+"-"+str(hour+1))

    df['period'] = period 

    return df
    