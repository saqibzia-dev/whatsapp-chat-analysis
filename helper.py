from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import streamlit as st

# gets Total no. of message,media,words,
@st.cache(suppress_st_warning=True)
def fetch_stats(selected_user,df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]
    # total no. of messages
    total_messages = df.shape[0]

    # total no. of words used
    words = []
    for message in df["message"]:
        words.extend(message.split(" "))
    total_words = len(words)
    # no. of media shared
    total_media = df[df["message"] == ' <Media omitted>\n'].shape[0]

    # no. of links shared
    # extracting number of links shared
    urls_list = []
    
    extractor = URLExtract()

    for message in df["message"]:
        # this will return urls in a list otherwise it return and empty list
        #print(extractor.find_urls(message))
        urls_list.extend(extractor.find_urls(message))
    #print(urls_list)
    links_shared = len(urls_list)

    return total_messages,total_words,total_media,links_shared

## getting most frequent users in the group
#@st.cache(suppress_st_warning=False)
def most_busiest_users(df):
    #most busiest users
    df2 = df[df["user"]!="group_notification"]

    x = df2['user'].value_counts().head(6)

    
    # per user contribution in the group
    # reset index convert the results into a dataframe
    contribution_df = round( (df2["user"].value_counts()/df2.shape[0])*100 ,2).reset_index().rename(columns = {"index":"name","user":"percent"})
    return x,contribution_df

# creating word cloud
@st.cache(suppress_st_warning=True)
def create_wordcloud(selected_user,df):
    
     # removing group message
    temp = df[df['user']!="group_notification"]
    # removing media omitted 
    temp = temp[temp['message']!=' <Media omitted>\n']
    # removing stopwords
    temp['message'] = temp['message'].apply(remove_stop_words)
    wc = WordCloud(width = 500,height = 300,min_font_size = 10,background_color = "white")
    # df.str.cat(sep) all values in the Series are concatenated into a single string with a given sep.
    df_wc = wc.generate(temp["message"].str.cat(sep = " "))
    return df_wc

# most common words used
#@st.cache(suppress_st_warning=False)
def most_common_words(selected_user,df):

        # removing group message
    temp = df[df['user']!="group_notification"]
    # removing media omitted 
    temp = temp[temp['message']!=' <Media omitted>\n']
    # removing stopwords
    f = open("stopword_hinglish.txt",'r',encoding = "utf-8")
    stop_words = f.read()
    f = open("stopwords-ur.txt",'r',encoding = "utf-8")
    stop_words_ur = f.read()
    #print(stop_words_ur) 
    #print(stopwords)
    #print(type(stopwords))
    words_without_stopwords = [] 
    for message in temp['message']:
        for word in message.lower().split():
            
            if word not in stop_words and word not in stop_words_ur:
                words_without_stopwords.append(word)

    # getting most 20 frequently used words
    
    #print(Counter(words_without_stopwords).most_common(20))
    df_most_common = pd.DataFrame(Counter(words_without_stopwords).most_common(20)).rename(columns = {0:'word',1:'frequency'})
    #df_most_common[0]
    return df_most_common

#remove stopwords

f = open("stopword_hinglish.txt",'r',encoding = "utf-8")
stop_words = f.read()
f = open("stopwords-ur.txt",'r',encoding = "utf-8")
stop_words_ur = f.read()
#@st.cache(suppress_st_warning=False)
def remove_stop_words(message):
    # removing stopwords
    
    #print(stop_words_ur) 
    #print(stopwords)
    #print(type(stopwords))
    words_without_stopwords = [] 
    
    for word in message.lower().split():
            
        if word not in stop_words and word not in stop_words_ur:
            words_without_stopwords.append(word)
    return " ".join(words_without_stopwords)

# emojis
#@st.cache(suppress_st_warning=False)
def emoji_helper(df):
    #counting what are the top emojis used

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])
    emojis_df = pd.DataFrame(Counter(emojis).most_common(len(emojis))).rename(columns = {0:"emoji",1:"count"})
    return emojis_df  

# get no. of messages sent in month
#@st.cache(suppress_st_warning=False)
def monthly_timeline(df):
    timeline = df.groupby(["year","month_num","month"]).count()["message"].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i]+"-"+str(timeline['year'][i]))
    timeline['time'] = time 
    return timeline
# get no. of messages sent daily
#@st.cache(suppress_st_warning=False)
def daily_timeline(df):
   #no. of messages daily  sent
    
    daily_timeline = df.groupby(["only_date"]).count()["message"].reset_index()
    return daily_timeline

# weekly activity map
#@st.cache(suppress_st_warning=False)
def weekly_activity_map(df):
    return df['day_name'].value_counts()

# month activity map
#@st.cache(suppress_st_warning=False)
def month_activity_map(df):
    return df['month'].value_counts()

# activity heatmap    
#@st.cache(suppress_st_warning=False)
def activity_heatmap(df):
    pivot_table = df.pivot_table(index = "day_name",columns = "period",values = "message",aggfunc = "count").fillna(0)
    return pivot_table
