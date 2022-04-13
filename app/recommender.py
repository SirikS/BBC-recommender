import pandas as pd
import numpy as np
import template as t
import streamlit as st
from itertools import cycle
from random import random
import string

def main_recommendations(df):
    df_shows = df[df['Episode_ID'] == 1]

    # continue watching
    next_episode = pd.read_csv('../recommendations/next_episode.csv')
    next_episode = next_episode[next_episode['user_id'] == st.session_state['user']['id']]
    if len(next_episode) > 0:
        st.subheader('Continue watching')
        t.recommendations(next_episode.merge(df, on='Content_ID').head(8), type='continue watching')


    # personal recommendations
    pred = t.rating_prediction(st.session_state['user']['id'])

    if not pred.empty:
      st.subheader('Recommended for you')
      t.recommendations(pred.merge(df_shows, on='Show_ID').head(8), type='personal recom')

    # top shows for the user's age
    if st.session_state['user']['age'] != 'Prefer not to say':
        best_age = pd.read_csv('../recommendations/age_best_reviewd.csv')
        best_age = best_age[best_age['age'] == st.session_state['user']['age']]
        st.subheader(f"Popular show for users of age {st.session_state['user']['age']}")
        t.recommendations(best_age.merge(df_shows, on='Show_ID').head(8), type='top shows')

    # top shows by gender
    if st.session_state['user']['gender'] in ['Male', 'Female']:
        best_gender = pd.read_csv('../recommendations/gender_best_reviewd.csv')
        best_gender = best_gender[best_gender['gender'] == st.session_state['user']['gender']]
        if st.session_state['user']['gender'] == 'Male':
            st.subheader('Popular shows amongst Men')
        if st.session_state['user']['gender'] == 'Female':
            st.subheader('Popular shows amongst Women')
        t.recommendations(best_gender.merge(df_shows, on='Show_ID').head(8), type='top shows')

    # user interests
    for genre in st.session_state['user']['content_types']:
        st.subheader(f"Because you're interested in {genre.capitalize()}")
        t.recommendations(df_shows[df_shows['Genre'] == genre].sample(8), type='Genre', linked_to=genre)
    
    # top shows overall
    best = pd.read_csv('../recommendations/total_best_reviewd.csv')
    st.subheader('Best reviewed shows')
    t.recommendations(best.merge(df_shows, on='Show_ID').head(8), type='top shows')

    st.subheader(f"Some of the best news shows")
    t.recommendations(df_shows[df_shows['Genre'] == 'news'].sample(8), type='Top news')

def content_recommendations(df, current_content):
    # recommend all content from current show
    # is there more shows?
    df_show = df[df['Show_ID'] == current_content['Show_ID']]
    if len(df_show) > 1:
        with st.expander("Select an episode from this show"):

            # are there more seasons and allow to select
            df_seasons = df_show.sort_values('Episode_ID').groupby('Season_no').head(1)
            if len(df_seasons) > 1:
                cols = cycle(st.columns(len(df_seasons)))
                for index, season in df_seasons.iterrows():
                    next(cols).button('Season: '+str(season['Season_no']), key=random(), on_click=t.select_content, args=(season['Content_ID'], 'Select season', current_content['Content_ID'], ))

            # select episode in a season if possible
            df_show = df[(df['Show_ID'] == current_content['Show_ID']) & (df['Season_no'] == current_content['Season_no'])].sort_values('Episode_ID')
            if len(df_show) > 1:
                st.subheader('Episodes in season: ' + str(current_content['Season_no']))
                if len(df_show) <= 8:
                    t.recommendations(df_show, type='Select episode', linked_to=current_content['Content_ID'], button='Episode_name')
                else:
                    dataframes = t.split_dataframe(df_show, chunk_size=8)
                    for dataframe in dataframes:
                        t.recommendations(dataframe, type='Select episode', linked_to=current_content['Content_ID'], button='Episode_name', len_rec=8)
            else:
                st.subheader('There are no other episodes in this season.')
    # similar show descriptions
    st.subheader('Shows or movies similar to ' + current_content['Title'])
    df_recom_kmeans = df[df['k_means'] == current_content['k_means']]
    df_recom_kmeans = df_recom_kmeans[df_recom_kmeans['Episode_ID'] == 1]
    df_recom_kmeans = df_recom_kmeans.sample(n=8, random_state = current_content['Content_ID'], replace=False)
    t.recommendations(df_recom_kmeans, type='Similar to', linked_to=current_content['Content_ID'])

    #third one being based on a similar genre
    st.subheader('Show or movies from the same genre as ' + current_content['Title'])
    df_recom_cat = df[(df['Genre'] == current_content['Genre']) & (df['Episode_ID'] == 1)]
    df_recom_cat = df_recom_cat.sample(n=min(len(df_recom_cat), 8), random_state = current_content['Content_ID'], replace=False)
    t.recommendations(df_recom_cat, type='Same genre', linked_to=current_content['Genre'])

def load_search(df):
    # usually when searching people will use lowercase, but to be sure I converted all strings to lowercase
    query = st.session_state['search query'].lower()
    query_exact = ' ' +query + ' '

    ## search for matches here, convert title and description to lowercase to avoid weird upper/lowercase dependent
    ##search results
    #make lower case, remove punctuation, add a space for the end to help with exact search
    df['title_low'] = df['Title'].str.lower() + ' '
    df['title_low'] = ' ' + df['title_low'].str.translate(str.maketrans('', '', string.punctuation)) + ' '

    df['description_low'] = df['Description'].str.lower()
    df['description_low'] = ' ' + df['description_low'].str.translate(str.maketrans('', '', string.punctuation)) + ' '

    #First search for exact word matches (aka ones followed by a space), then non exact matches (partial words)
    df_title_search = df[df['title_low'].str.contains(query_exact)]
    df_title_search = df_title_search[df_title_search['Episode_ID'] == 1]
    if len(df_title_search) < 8:
        df_title_search_part = df[df['title_low'].str.contains(query)]
        df_title_search_part = df_title_search_part[df_title_search_part['Episode_ID'] == 1]
        df_title_search_part = df_title_search_part.sample(min(len(df_title_search_part), (8 - len(df_title_search))))
        df_title_search = df_title_search.append(df_title_search_part)
        df_title_search = df_title_search.drop_duplicates(subset=['Show_ID'])



    df_description_search = df[df['description_low'].str.contains(query_exact)]
    if len(df_description_search) < 8:
        df_description_search_part = df[df['description_low'].str.contains(query)]
        df_description_search_part = df_description_search_part.sample(min(len(df_description_search_part), (8 - len(df_description_search))))
        df_description_search = df_description_search.append(df_description_search_part)
        df_description_search = df_description_search.drop_duplicates(subset=['Episode_ID'])




    ##show the search results
    st.header('Because you searched for \'' + query + '\'')

    # Search results based on title
    st.subheader('Shows or movies that have \'' + query + '\' in their title')
    if len(df_title_search) > 0:
        t.recommendations(df_title_search, type='Title search', linked_to=query)
    else:
        st.text('No shows or movies that have \'' + query + '\' in their title were found ')

    # Search results based on description
    st.subheader('Episodes that contain \'' + query + '\' in their description')
    if len(df_description_search) > 0:
        t.recommendations(df_description_search, type='Description search', linked_to=query, button='both')
    else:
        st.text('No shows or movies that contain \'' + query + '\' in their description were found')

    # stop so the normal recommendations are not loaded. 
    st.stop()
