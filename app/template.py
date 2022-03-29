import streamlit as st
from random import random
import datetime
import csv
import pandas as pd
from ast import literal_eval

def activity(activity, id=None, attribute_link=None, attribute_value=None, user_id=None):
  if not user_id:
    user_id = st.session_state['user']['id']
  data = {'content_id': id, 'activity': activity, 'attribute_link':attribute_link, 'attribute_value': attribute_value, 
  'user_id': user_id, 'datetime': str(datetime.datetime.now())}
  
  # only turn of if csv file has to be made
  # with open('../data/activities.csv', 'w') as f:
  #   csv.writer(f).writerow(data.keys())

  # store in csv
  with open('../data/activities.csv', 'a') as f:
    csv.writer(f).writerow(data.values())

def tile_item(column, item, type, linked_to):
  with column:
    st.image(item['Image'], use_column_width='always')
    st.button(item['Title'], key=random(), on_click=select_content, args=(item['ID'], type, linked_to))

def recommendations(df, type='unknown', linked_to=None):

  # check the number of items
  nbr_items = df.shape[0]

  if nbr_items != 0:    

    # create columns with the corresponding number of items
    columns = st.columns(nbr_items)

    # convert df rows to dict lists
    items = df.to_dict(orient='records')

    # apply tile_item to each column-item tuple (created with python 'zip')
    any(tile_item(x[0], x[1], type, linked_to) for x in zip(columns, items))

def login(user):
  # loging and store activity
  st.session_state['user'] = user
  activity(activity='login')

def logout():
  # unload content if loaded
  if 'index' in st.session_state:
    unload_content()
  
  # store activity
  activity(activity='logout')

  # logout
  del st.session_state['user']
  st.session_state['logout'] = True

def select_content(show_id, type, linked_to):  
  # unload content if loaded
  if 'index' in st.session_state:
    unload_content()

  # load content and log
  st.session_state['index'] = show_id
  activity(activity='select content', id=show_id, attribute_link=type, attribute_value=linked_to)

def unload_content():
  # log unloading, and reset index
  activity(activity='unload content', id=st.session_state['index'])
  del st.session_state['index']

def rating_callback(id):
  # store the rating
  activity(activity='content_rating', id=id, attribute_value=st.session_state.content_rating)

def create_account_form():
  with st.form('new account'):
    username_input = st.text_input('Preferred username', key='new_username')
    password_input = st.text_input('Password', type='password', key='new_password')
    gender = st.selectbox('What is you gender?', ('Male', 'Female', 'Other'), key='new_gender')
    age = st.selectbox('What is you age', ('0-9', '10-17', '18-29', '30-49', '50-64', '65+', 'Prefer not to say'), index=2,  key='new_age')
    options = st.multiselect('What kind of content do you like?', pd.read_csv('../data/BBC_proccessed.csv').Genre.unique(), key='content_types')
    submit_button = st.form_submit_button("Create account", on_click=create_account)

def create_account():
  users = pd.read_csv('../data/users.csv', converters={"content_types": literal_eval})
  username = st.session_state.new_username
  password = st.session_state.new_password
  if not username:
    st.error('Please fill in a username')
  elif not password:
    st.error('Please fill in a password')
  elif username in users['name'].values:
    st.error('Username already taken')
  else:
    gender = st.session_state.new_gender
    age = st.session_state.new_age
    content_types =str(st.session_state.content_types)

    new_id = users.id.max() + 1

    new_user = pd.DataFrame([{'name': username, 'id': new_id, 'password':password, 'age': age, 
    'gender': gender, 'content_types': content_types}])
    new_user['content_types'] = new_user['content_types'].apply(literal_eval)

    users = pd.concat([users, new_user])

    # store the new user
    users.to_csv('../data/users.csv', index=False)

    activity(activity='create_account', user_id=new_id)
    st.session_state['account create'] = False
    login(new_user.loc[0])

  
  