import streamlit as st
from helper import activity_heatmap, fetch_stats
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(page_title = "Whatsapp Chat Analysis",layout='wide')
st.sidebar.title("Whatsapp Chat Analysis")
uploaded_file = st.sidebar.file_uploader("Upload Chat",["txt"])
if uploaded_file is not None:
    #this provide data in byte stream
    bytes_data = uploaded_file.getvalue()
    # converting byte stream into string
    data = bytes_data.decode("utf-8")
    #st.text(data)
    df = preprocessor.preprocess(data)
    #st.dataframe(df)

    #fetching unique users
    user_list = df['user'].unique().tolist()
    user_list.remove("group_notification")
    user_list.sort()
    #st.text(user_list)
    user_list.insert(0,"Overall")
    selected_user = st.sidebar.selectbox("Analysis based upon",user_list)
    
    
    if st.sidebar.button("Show Analysis"):
        st.subheader(selected_user + " Chat Analysis")

        #stats Area

        total_messages,total_words,total_media,links_shared = helper.fetch_stats(selected_user,df)
        #st.title("Statistics")
        cols = st.columns(4)

        with cols[0]:
            st.text("Total Messages")
            st.text(total_messages)
        with cols[1]:
            st.text("Total Words")
            st.text(total_words)
        with cols[2]:
            st.text("Media Shared")
            st.text(total_media)
        with cols[3]:
            st.text("Links Shared")
            st.text(links_shared)
        
        

        
        if selected_user != "Overall":
            df = df[df["user"] == selected_user]
        
        #daily messages sent
        #st.subheader("Daily Messages Sent")
        #plt.style.use('ggplot')
        
        daily_timeline = helper.daily_timeline(df)
        # fig,ax = plt.subplots()
        # ax.plot(daily_timeline["only_date"],daily_timeline["message"])
        # plt.xticks(rotation = "vertical")
        # st.pyplot(fig) 
        fig = px.line(daily_timeline, x="only_date", y="message", title='Daily Messages Sent')
        fig.update_layout(width=650, height=450, plot_bgcolor='rgb(205, 209, 208)')
        fig.data[0].line.color = 'rgb(219, 70, 29)'
        # fig = px.bar(timeline, y='message', x='time', text='time')
        # fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        # fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide') 
        st.plotly_chart(fig)



        
        #monthly timeline
        #st.subheader("Monthly Messages Sent")
        plt.style.use('ggplot')
        timeline = helper.monthly_timeline(df)
        # fig,ax = plt.subplots()
        # ax.plot(timeline["time"],timeline["message"])
        # plt.xticks(rotation = "vertical")
        # st.pyplot(fig)
        fig = px.line(timeline, x="time", y="message", title='Monthly Messages Sent')
        fig.update_layout(width=650, height=450, plot_bgcolor='rgb(205, 209, 208)')
        fig.data[0].line.color = 'rgb(227, 121, 23)'
        # fig = px.bar(timeline, y='message', x='time', text='time')
        # fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        # fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide') 
        st.plotly_chart(fig)

        #activity map
        st.title("Activity map")
        activity_cols = st.columns(2)
        with activity_cols[0]:
            st.header("Most Busy Day")
            busy_day = helper.weekly_activity_map(df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values)
            plt.xticks(rotation = "vertical")
            st.pyplot(fig)
        
        with activity_cols[1]:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(df)
            fig,ax = plt.subplots()
            ax.bar(busy_month.index,busy_month.values,color = "orange")
            plt.xticks(rotation = "vertical")
            st.pyplot(fig)

        # activity heatmap
        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(df)
        fig,ax = plt.subplots(figsize = (20,6))
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # most busiest users group level
        if selected_user =="Overall":
            st.title("Most Busiest Users:")
            col_plot = st.columns(2)

            x,contribution_df = helper.most_busiest_users(df)
            plt.style.use('fivethirtyeight')
            name = x.index
            count = x.values
            fig,ax = plt.subplots()
            ax.barh(name,count)
            #plt.xticks(rotation = "vertical")
            plt.title("Top  Busiest users")
            #plt.show()
            
            with col_plot[0]:
                st.pyplot(fig)
            with col_plot[1]:
                st.dataframe(contribution_df)
                #st.write(contribution_df)
            
        #word cloud
        st.title(" Word Cloud:")
        df_wc = helper.create_wordcloud(selected_user,df)
        plt.style.use('classic')
        fig,ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        #most common words used
        st.title("Most common words")
        df_most_common = helper.most_common_words(selected_user,df)
        #st.dataframe(df_most_common)
        plt.style.use("ggplot")
        fig,ax = plt.subplots()
        ax.barh(df_most_common["word"],df_most_common["frequency"])
        # fig = go.Figure(go.Bar(
        #     x=df_most_common["frequency"],
        #     y=df_most_common["word"],
        #     orientation='h'))
        # st.plotly_chart(fig)
        st.pyplot(fig)

        #emoji analysis
        st.title("Emoji Analysis")
        emoji_cols = st.columns(2)
        
        
        emojis_df = helper.emoji_helper(df)
        if not emojis_df.empty :
            with emoji_cols[0]:
                st.dataframe(emojis_df)
            with emoji_cols[1]:
                fig,ax = plt.subplots()
                ax.pie(emojis_df["count"].head(),labels = emojis_df["emoji"].head(),autopct = "%0.2f")
                st.pyplot(fig)
                #fig = px.pie(emojis_df.head(),values = "count",names = "emoji")
                #st.plotly_chart(fig)



