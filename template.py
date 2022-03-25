import streamlit as st
from random import random
from PIL import Image
import requests


def select_show(show_id):  
  st.session_state['index'] = show_id



def tile_item(column, item):
  with column:

    st.image(item['Image'], use_column_width='always')
    st.button(item['Title'], key=random(), on_click=select_show, args=(item['ID'], ))
    #st.caption(item['titles'])

def recommendations(df):

  # check the number of items
  nbr_items = df.shape[0]

  if nbr_items != 0:    

    # create columns with the corresponding number of items
    columns = st.columns(nbr_items)

    # convert df rows to dict lists
    items = df.to_dict(orient='records')

    # apply tile_item to each column-item tuple (created with python 'zip')
    any(tile_item(x[0], x[1]) for x in zip(columns, items))


