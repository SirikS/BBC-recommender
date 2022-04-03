import pandas as pd
import numpy as np
import template as t
import streamlit as st

def main_recommendations(df):

    # user interests
    for genre in st.session_state['user']['content_types']:
        st.subheader(f"Because you're interested in {genre.capitalize()}")
        t.recommendations(df[df['Genre'] == genre].sample(8), type='Genre', linked_to=genre)

    st.subheader(f"Some of the top news shows")
    t.recommendations(df[df['Genre'] == 'news'].sample(8), type='Top news')

def content_recommendations(df, current_content):
    # similar show descriptions
    st.subheader('Shows or movies similar to ' + current_content['Title'])
    df_recom_kmeans = df[df['k_means'] == current_content['k_means']]
    df_recom_kmeans = df_recom_kmeans.sample(n=8, random_state = current_content['ID'], replace=False)
    t.recommendations(df_recom_kmeans, type='Similar to', linked_to=current_content['ID'])

    #third one being based on a similar genre
    st.subheader('Show or movies from the same genre as ' + current_content['Title'])
    df_recom_cat = df[df['Genre'] == current_content['Genre']]
    df_recom_cat = df_recom_cat.sample(n=8, random_state = current_content['ID'], replace=False)
    t.recommendations(df_recom_cat, type='Same genre', linked_to=current_content['Genre'])

def load_search():
    # usually when searching people will use lowercase, but to be sure I converted all strings to lowercase
    query = st.session_state['search query']
    df = pd.read_csv('../data/BBC_proccessed.csv')

    ## search for matches here, convert title and description to lowercase to void weird upper/lowercase dependent
    ##search results
    df['title_low'] = df['Title'].str.lower() + ' '
    df_title_search = df[df['title_low'].str.contains(query.lower())]
    df_title_search = df_title_search.sample(min(len(df_title_search), 8))

    df['description_low'] = df['Description'].str.lower()
    df_description_search = df[df['description_low'].str.contains(query.lower())]
    df_description_search = df_description_search.sample(min(len(df_description_search),8))

    ##show the search results
    st.header('Because you searched for \'' + query + '\'')

    # Search results based on title
    st.subheader('Shows or movies that have \'' + query + '\' in their title')
    if len(df_title_search) > 0:
        t.recommendations(df_title_search, type='Search')
    else:
        st.text('No shows or movies that have \'' + query + '\' in their title were found ')

    # Search results based on description
    st.subheader('Shows or movies that contain \'' + query + '\' in their description')
    if len(df_description_search) > 0:
        t.recommendations(df_description_search, type='Search')
    else:
        st.text('No shows or movies that contain \'' + query + '\' in their description were found')

    # stop so the normal recommendations are not loaded. 
    st.stop()
