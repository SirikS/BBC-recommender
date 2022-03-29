import pandas as pd
import numpy as np
import template as t
import streamlit as st

def main_recommendations(df):

    # user interests
    for genre in st.session_state['user']['content_types']:
        st.subheader(f"Because you're interested in {genre.capitalize()}")
        t.recommendations(df[df['Genre'] == genre].sample(10), type='Genre', linked_to=genre)

    st.subheader(f"Some of the top news shows")
    t.recommendations(df[df['Genre'] == 'news'].sample(10), type='Top news')

def content_recommendations(df, current_content):
    # similar show descriptions
    st.subheader('Shows or movies similar to ' + current_content['Title'])
    df_recom_kmeans = df[df['k_means'] == current_content['k_means']]
    df_recom_kmeans = df_recom_kmeans.sample(n=7, random_state = current_content['ID'], replace=False)
    t.recommendations(df_recom_kmeans, type='Similar to', linked_to=current_content['ID'])

    #third one being based on a similar genre
    st.subheader('Show or movies from the same genre as ' + current_content['Title'])
    df_recom_cat = df[df['Genre'] == current_content['Genre']]
    df_recom_cat = df_recom_cat.sample(n=8, random_state = current_content['ID'], replace=False)
    t.recommendations(df_recom_cat, type='Same genre', linked_to=current_content['Genre'])
