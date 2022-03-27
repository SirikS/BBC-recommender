import streamlit as st
import pandas as pd
import numpy as np
from random import random

import template as t
import recommender as r
# import authenticate as a

#set page layout and load in the dataset 
st.set_page_config(layout='wide')
df_users = pd.read_json('../data/users.json')

# Login precedure
# logout session state is used so that one is not logged in directly after logging out
if 'logout' not in st.session_state:
  st.session_state['logout'] = False

if 'user' not in st.session_state:
  # create some room for login
  placeholder = st.empty()
  with placeholder.container():
    # collect user data
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    # check if both are entered
    if not username or not password:
      st.stop()
    # does the username exist
    elif username not in df_users['name'].unique():
      st.warning('Invalid username')
      st.stop()
    # validate password
    elif password != df_users[df_users['name'] == username].iloc[0]['password']:
      st.warning('Invalid password')
      st.stop()
    # login if all is correct and not just logged out
    elif (not st.session_state['logout']) and (password == df_users[df_users['name'] == username].iloc[0]['password']):
      t.login(df_users[df_users['name'] == username].iloc[0])
    # else they have must just logged out, so reset the logout parameter
    else:
      st.session_state['logout'] = False
      st.success('Logout succesfull')
      st.stop()
  placeholder.empty()
  st.success(f"Welcome {st.session_state['user']['name']}, have a look around!")


# if logged in: load all content
df_bbc = pd.read_csv('../data/BBC_proccessed.csv')

# menu bar
col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
if 'index' in st.session_state:
  with col1:
    st.button("Back to recommender", key=random(), on_click=t.unload_content)
else:
  # could use this room for search bar/other buttons
  pass

with col4:
  st.button("Logout", key=random(), on_click=t.logout)

# if not looking at content, load front page recommendations
if 'index' not in st.session_state:
  r.main_recommendations(df_bbc)
  st.stop()

# else on content page, so load content
df_current_content = df_bbc[df_bbc['ID'] ==  st.session_state['index']].iloc[0]

# display content
col1, col2 = st.columns(2)
with col1:
  st.image(df_current_content['Image'])                     
with col2:
  st.title(df_current_content['Title'])
  st.markdown(df_current_content['Description'])
  st.text('Genre:' + df_current_content['Genre'])

  # user rating
  with st.form('rating'):
    slider_rating = st.slider('Rate this content', min_value=0.0, max_value=5.0, step=0.1, key='content_rating')
    submit_button = st.form_submit_button("Submit rating", on_click=t.rating_callback, args=(st.session_state['index'], ))

# on content page, make similar type of content recommendations
r.content_recommendations(df_bbc, df_current_content)


