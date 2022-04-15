# script to calculate user interactions
# - watchtime
# - latest rating

# and to precalculate recommendations
# - top viewed
# - top reviewed
# - top reviewed age
# - top reviewed gender
# - continue watching

import pandas as pd
import streamlit as st
from ast import literal_eval

def do_calculations():
    """Run all used precalculations"""
    # run activity calculations
    watchtime()
    rating_dataset()

    # create recommendations
    # total_best_reviewed()
    top_viewed()
    age_best_reviewed()
    gender_best_reviewed()
    continue_watching()


# create watchtime dataset
def watchtime():
    """Calculate the watchtime a user spent on a content item based on opening and closing content"""
    # load relevant activities
    df = pd.read_csv('../data/activities.csv', sep=',')
    df = df[df['activity'].isin(['select content', 'unload content'])].sort_values(by=['user_id', 'datetime'])

    # correct format
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['content_id'] = df['content_id'].astype(int)

    # join with the next load/unload activity
    df[['content_id2', 'activity2', 'user_id2', 'datetime2']] = df.shift(-1)[['content_id', 'activity', 'user_id', 'datetime']]

    # only store if join was correct
    df = df[(df['content_id'] == df['content_id2']) & (df['user_id'] == df['user_id2'])& (df['activity'] != df['activity2'])]

    # calculate watch time
    df['watch_time'] = abs((df['datetime2'] - df['datetime']).dt.total_seconds())

    # select only relevant features
    df = df[['user_id', 'content_id', 'watch_time']]

    # combine all user-content watches and sum total watch time
    df = df.groupby(['user_id', 'content_id'])['watch_time'].sum().reset_index()

    # store total watch time
    df.to_csv('../data/total_watch_time.csv', index=False)

# create ratings dataset
def rating_dataset():
    """Collect most recent rating and store in the ratings dataset"""
    # load ratings
    activities = pd.read_csv('../data/activities.csv')
    ratings = activities[activities['activity'] == 'content rating']

    # select most recent rating
    ratings = ratings.sort_values('datetime', ascending=False).groupby(['content_id', 'user_id']).head(1)

    # reformat and save
    ratings = ratings[['user_id', 'content_id', 'attribute_value']].rename({'attribute_value':'rating'}, axis=1)
    ratings['content_id'] = ratings['content_id'].astype(int)
    ratings.to_csv('../data/ratings.csv', index=False)

def weighted_rating(x, m, C):
    """Function for weighted recommendations"""
    v = x['count']
    R = x['mean']
    return (v/(v+m) * R) + (m/(m+v) * C)

def top_viewed():
    """Precalculate recommendations based on most watchtime"""
    watchtime = pd.read_csv('../data/total_watch_time.csv')
    content = pd.read_csv('../data/BBC_episodes.csv')
    users = pd.read_csv('../data/users.csv',converters={"content_types": literal_eval}, dtype={'id': int})

    temp = watchtime.merge(content, left_on='content_id', right_on='Content_ID')[['user_id', 'Content_ID', 'Show_ID', 'Episode_ID', 'watch_time']]
    df = temp.merge(users, left_on='user_id', right_on='id')[['user_id', 'Content_ID', 'Show_ID', 'Episode_ID', 'watch_time', 'age', 'gender']]
    del temp

    df = df.groupby(['Show_ID'])['watch_time'].agg(['mean', 'count']).reset_index()

    # C is the mean vote across the whole report
    C = df['mean'].mean()

    # m is the minimum votes required to be listed in the chart;
    m = df['count'].quantile(0.99)

    df['weight'] = df.apply(weighted_rating, args= (C, m, ), axis=1)

    df_total = df.sort_values('weight', ascending=False).head(16)[['Show_ID', 'weight']]

    df_total.to_csv('../recommendations/top_viewed.csv', index=False)

def total_best_reviewed():
    """Precalculate recommendations based on best weighted reviews"""
    ratings = pd.read_csv('../data/ratings.csv')
    content = pd.read_csv('../data/BBC_episodes.csv')
    users = pd.read_csv('../data/users.csv',converters={"content_types": literal_eval}, dtype={'id': int})

    temp = ratings.merge(content, left_on='content_id', right_on='Content_ID')[['user_id', 'Content_ID', 'Show_ID', 'Episode_ID', 'rating']]
    df = temp.merge(users, left_on='user_id', right_on='id')[['user_id', 'Content_ID', 'Show_ID', 'Episode_ID', 'rating', 'age', 'gender']]
    del temp

    df = df.groupby(['Show_ID'])['rating'].agg(['mean', 'count']).reset_index()

    # C is the mean vote across the whole report
    C = df['mean'].mean()

    # m is the minimum votes required to be listed in the chart;
    m = df['count'].quantile(0.99)

    df['weight'] = df.apply(weighted_rating, args= (C, m, ), axis=1)

    df_total = df.sort_values('weight', ascending=False).head(16)[['Show_ID', 'weight']]
    df_total.to_csv('../recommendations/total_best_reviewd.csv', index=False)

def age_best_reviewed():
    """Precalculate weighted recommendations for all age groups"""
    ratings = pd.read_csv('../data/ratings.csv')
    content = pd.read_csv('../data/BBC_episodes.csv')
    users = pd.read_csv('../data/users.csv',converters={"content_types": literal_eval}, dtype={'id': int})
    temp = ratings.merge(content, left_on='content_id', right_on='Content_ID')[['user_id', 'Content_ID', 'Show_ID', 'Episode_ID', 'rating']]
    df = temp.merge(users, left_on='user_id', right_on='id')[['user_id', 'Content_ID', 'Show_ID', 'Episode_ID', 'rating', 'age', 'gender']]
    del temp

    # users
    df = df.groupby(['Show_ID', 'age'])['rating'].agg(['mean', 'count']).reset_index()

    # C is the mean vote across the whole report
    C = df['mean'].mean()

    # m is the minimum votes required to be listed in the chart;
    m = df['count'].quantile(0.99)

    df['weight'] = df.apply(weighted_rating, args= (C, m, ), axis=1)

    df_age = df.sort_values(['age', 'weight'], ascending=False).groupby('age').head(16)[['Show_ID', 'age', 'weight']]
    df_age.to_csv('../recommendations/age_best_reviewd.csv', index=False)

def gender_best_reviewed():
    """Precalculate weighted recommendations for every gender"""
    ratings = pd.read_csv('../data/ratings.csv')
    content = pd.read_csv('../data/BBC_episodes.csv')
    users = pd.read_csv('../data/users.csv',converters={"content_types": literal_eval}, dtype={'id': int})

    temp = ratings.merge(content, left_on='content_id', right_on='Content_ID')[['user_id', 'Content_ID', 'Show_ID', 'Episode_ID', 'rating']]
    df = temp.merge(users, left_on='user_id', right_on='id')[['user_id', 'Content_ID', 'Show_ID', 'Episode_ID', 'rating', 'age', 'gender']]
    del temp

    # users
    df = df.groupby(['Show_ID', 'gender'])['rating'].agg(['mean', 'count']).reset_index()

    # C is the mean vote across the whole report
    C = df['mean'].mean()

    # m is the minimum votes required to be listed in the chart;
    m = df['count'].quantile(0.99)

    df['weight'] = df.apply(weighted_rating, args= (C, m, ), axis=1)

    df_gender = df.sort_values(['gender', 'weight'], ascending=False).groupby('gender').head(16)[['Show_ID', 'gender', 'weight']]
    df_gender.to_csv('../recommendations/gender_best_reviewd.csv', index=False)

def continue_watching():
    """Precalculate recommendations to continue watching. Last reviewed episode is the last viewed episode."""
    ratings = pd.read_csv('../data/ratings.csv')
    content = pd.read_csv('../data/BBC_episodes.csv')

    latest_show = ratings.merge(content, left_on='content_id', right_on='Content_ID')[['user_id', 'Content_ID', 'Show_ID', 'Episode_ID', 'rating']]
    latest_show = latest_show.groupby(['user_id', 'Show_ID']).agg({'Episode_ID':max, 'rating':'mean'}).reset_index()
    latest_show['next_episode'] = latest_show['Episode_ID'] + 1

    next_show = latest_show.merge(content, left_on=['Show_ID', 'next_episode'], right_on=['Show_ID', 'Episode_ID'], how='inner')
    next_show = next_show[['user_id', 'Content_ID', 'rating']]
    next_show = next_show[next_show['rating'] >= 3]
    next_show.to_csv('../recommendations/next_episode.csv', index=False)



