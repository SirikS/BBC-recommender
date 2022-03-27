import streamlit as st
from random import random
# from PIL import Image
# import requests
import datetime
import csv

def activity(activity, id=None, attribute_link=None, attribute_value=None):
  data = {'content_id': id, 'activity': activity, 'attribute_link':attribute_link, 'attribute_value': attribute_value, 
  'user_id': int(st.session_state['user']['id']), 'datetime': str(datetime.datetime.now())}
  
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
  