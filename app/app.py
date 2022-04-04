from turtle import onclick
import streamlit as st
import pandas as pd
import numpy as np
from random import random
from ast import literal_eval

import template as t
import recommender as r

#set page layout and load in the dataset 
st.set_page_config(layout='wide')
df_users = pd.read_csv('../data/users.csv', converters={"content_types": literal_eval}, dtype={'id': int})


### setup some session state values
if 'incognito' not in st.session_state:
  st.session_state['incognito'] = False

if 'open profile' not in st.session_state:
  st.session_state['open profile'] = False

if 'load search' not in st.session_state:
  st.session_state['load search'] = False

### login procedure
# account creation session is used so the form does not dissapear if the user gave wrong input in the form
if 'account create' not in st.session_state:
  st.session_state['account create'] = False

if 'user' not in st.session_state:
  t.login_page()


### if logged in, see if the profile is opened
if st.session_state['open profile']:
  t.profile()

### menu bar
col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
# on content after search
if 'index' in st.session_state and st.session_state['load search']:
  with col1:
    st.title('')
    st.button("Back to search", key=random(), on_click=t.unload_content)
# on content from main recommender
elif 'index' in st.session_state and not st.session_state['load search']:
  with col1:
    st.title('')
    st.button("Back to recommender", key=random(), on_click=t.unload_content)
# on search
elif (not 'index' in st.session_state) and st.session_state['load search']:
  with col1:
    st.title('')
    st.button("Back to recommender", key=random(), on_click=t.stop_search)
else:
  pass

with col2:
  st.title('')
  st.checkbox('Incognito session', key='incognito')
with col3:
  searchbar = st.text_input('Search for an item', placeholder='For example: Dance Passion', key='search', on_change=t.set_search)
with col4:
  st.title('')
  st.button('View profile', on_click=t.open_profile)

### recommendations
df_episode = pd.read_csv('../data/BBC_episodes.csv')

## front page recommendations
if 'index' not in st.session_state:
  if st.session_state['load search']:
    r.load_search(df_episode)
  r.main_recommendations(df_episode)
  st.stop()

## content page
df_current_content = df_episode[df_episode['Content_ID'] ==  st.session_state['index']].iloc[0]

# display content
col1, col2 = st.columns(2)
with col1:
  st.image(df_current_content['Image'])                     
with col2:
  st.title(df_current_content['Title'])
  st.subheader(df_current_content['Season+Episode'])
  st.markdown(df_current_content['Description'])
  st.text('Genre:' + df_current_content['Genre'])

  # user rating
  with st.form('rating'):
    slider_rating = st.slider('Rate this content', min_value=0, max_value=5, step=1, key='content_rating')
    submit_button = st.form_submit_button("Submit rating", on_click=t.rating_callback, args=(st.session_state['index'], ))

# on content page, make similar type of content recommendations
r.content_recommendations(df_episode, df_current_content)



