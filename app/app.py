# main application that triggers all helper functions and loads on refresh

import streamlit as st
import pandas as pd
import numpy as np
from random import random
from ast import literal_eval
from itertools import cycle
pd.options.mode.chained_assignment = None

import template as t
import recommender as r

# SETUP PAGE CONFIG AND LOAD USER DATA
#set page layout and load in the dataset 
st.set_page_config(layout='wide')
df_users = pd.read_csv('../data/users.csv', converters={"content_types": literal_eval}, dtype={'id': int})

# INITIATE OPENING PARAMETERs
if 'incognito' not in st.session_state:
  st.session_state['incognito'] = False
if 'open profile' not in st.session_state:
  st.session_state['open profile'] = False
if 'load search' not in st.session_state:
  st.session_state['load search'] = False

# LOGIN PROCEDURE
# account creation session is used so the form does not dissapear if the user gave wrong input in the form
if 'account create' not in st.session_state:
  st.session_state['account create'] = False

if 'user' not in st.session_state:
  t.login_page()


# LOAD PROFILE PAGE WHEN OPENED
if st.session_state['open profile']:
  t.profile()

# LOAD TOP BAR MENU
col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
# if on content after search, make button to go back to search
if 'index' in st.session_state and st.session_state['load search']:
  with col1:
    st.title('')
    st.button("Back to search", key=random(), on_click=t.unload_content)
# on content from main recommender make go back to recommender button
elif 'index' in st.session_state and not st.session_state['load search']:
  with col1:
    st.title('')
    st.button("Back to recommender", key=random(), on_click=t.unload_content)
# on search page, make button to go back to recommender butoon
elif (not 'index' in st.session_state) and st.session_state['load search']:
  with col1:
    st.title('')
    st.button("Back to recommender", key=random(), on_click=t.stop_search)
else:
  pass
# allow the user to go incognito, this stops the system from logging clicks
with col2:
  st.title('')
  st.checkbox('Incognito session', key='incognito')
# search bar
with col3:
  searchbar = st.text_input('Search for an item', placeholder='For example: Dance', key='search', on_change=t.set_search)
with col4:
# got to profile button
  st.title('')
  st.button('View profile', on_click=t.open_profile)

# LOAD EPISODE DATASET
df_episode = pd.read_csv('../data/BBC_episodes.csv', parse_dates=['Date'])
df_episode['Season_no'] = pd.to_numeric(df_episode['Season_no'], errors='ignore')
df_episode['Episode'] = pd.to_numeric(df_episode['Episode'], errors='ignore')

# LOAD FRONT PAGE RECOMMENDATIONS (COLLABORATIVE FILTERING)
if 'index' not in st.session_state:
  if st.session_state['load search']:
    r.load_search(df_episode)
  r.main_recommendations(df_episode)
  st.stop()

# ELSE ON CONTENT PAGE
df_current_content = df_episode[df_episode['Content_ID'] ==  st.session_state['index']].iloc[0]

# DISPLAY CURRENT CONTENT
# picture, title, description etc. 
col1, col2 = st.columns(2)
with col1:
  st.image(df_current_content['Image'])                     
with col2:
  st.title(df_current_content['Title'])
  st.subheader(df_current_content['Season+Episode'])
  st.markdown(df_current_content['Description'])
  st.caption(f"Duration: {df_current_content['Duration']} minutes | Genre: {df_current_content['Genre']}")

  df_show = df_episode[df_episode['Show_ID'] == df_current_content['Show_ID']]
  df_next = df_show[df_show['Episode_ID'] == (df_current_content['Episode_ID'] + 1)]
  if len(df_next) == 1:
    st.button('Next episode', key=random(), on_click=t.select_content, args=(df_next['Content_ID'].iloc[0], 'Next episode', df_current_content['Content_ID']))

  # create a user rating form
  with st.form('rating'):
    try:
      df_ratings = pd.read_csv('../data/ratings.csv', dtype={'rating':int})
      current_rating = df_ratings[(df_ratings['user_id'] == st.session_state['user']['id']) & (df_ratings['content_id'] == st.session_state['index'])].iloc[0]['rating']
    except:
      current_rating = 0
    slider_rating = st.slider('Rate this content', min_value=0, max_value=5, value=int(current_rating), step=1, key='content_rating')
    submit_button = st.form_submit_button("Submit rating", on_click=t.rating_callback, args=(st.session_state['index'], ))

# ALSO SHOW CONTENT BASED RECOMMENDATIONS
r.content_recommendations(df_episode, df_current_content)



