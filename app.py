import streamlit as st
import pandas as pd
import template as t
import numpy as np
from random import random
from numpy import genfromtxt

#######################################################################
#set page layout and load in the dataset 
st.set_page_config(layout='wide')
df_bbc = pd.read_csv('BBC_proccessed.csv')

#set a session state for if there is none yet
if 'index' not in st.session_state:
    st.session_state['index'] = 281






######################################################################

#make a setable session state depending on clicks, add this session state to a list of shows.
df_bbc_small = df_bbc[df_bbc['ID'] ==  st.session_state['index']]



####################################################################
##Make a header which shows the book and a description
#split the header in 2 columns
col1, col2 = st.columns(2)

#show the image in one column and the descriptions in the other
with col1:
  st.image(df_bbc_small['Image'].iloc[0])
                        
with col2:
  st.title(df_bbc_small['Title'].iloc[0])
  st.markdown(df_bbc_small['Description'].iloc[0])
  st.text('Genre:' + df_bbc_small['Genre'].iloc[0])




############################################
###Make a few subheaders
  #First one being recommendations for you
    #for this I track the shows being 'watched' (I take the extreme oversimplification of clicked = watched here for arguments sake)
    #then I calculate the highest and lowest sum of cosine distances to shows that were watched





    #second one being similar show descriptions
st.subheader('Shows or movies similar to ' + df_bbc_small['Title'].iloc[0])
df_recom_kmeans = df_bbc[df_bbc['k_means'] == df_bbc_small['k_means'].iloc[0]]
df_recom_kmeans = df_recom_kmeans.sample(n=7, random_state = df_bbc_small['ID'], replace=False)
t.recommendations(df_recom_kmeans)


    #third one being based on a similar genre

st.subheader('Show or movies from the same genre as ' + df_bbc_small['Title'].iloc[0])

df_recom_cat = df_bbc[df_bbc['Genre'] == df_bbc_small['Genre'].iloc[0]]
df_recom_cat = df_recom_cat.sample(n=8, random_state = df_bbc_small['ID'], replace=False)
t.recommendations(df_recom_cat)




