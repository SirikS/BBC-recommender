# Script that consists of all helper functions of the application
# - activity logging
# - make recommendations
# - login
# - logout
# - account creation 
# - account changes (update profile/dowload data/remove data/etc.)
# - searching
# - personal recommendation algorithm

import streamlit as st
from random import random
import datetime
import csv
import pandas as pd
pd.options.mode.chained_assignment = None
from ast import literal_eval
import interaction_calculations as calc
from sklearn.neighbors import NearestNeighbors

def activity(activity, id=None, attribute_link=None, attribute_value=None, user_id=None):
  if st.session_state.incognito and id != None:
    return
  
  if not user_id:
    user_id = st.session_state['user']['id']
  data = {'content_id': id, 'activity': activity, 'attribute_link':attribute_link, 'attribute_value': attribute_value, 
  'user_id': user_id, 'datetime': str(datetime.datetime.now())}
  
  # only turn of if csv file has to be newly made
  # with open('../data/activities.csv', 'w') as f:
  #   csv.writer(f).writerow(data.keys())

  # store in csv
  with open('../data/activities.csv', 'a') as f:
    csv.writer(f).writerow(data.values())

def tile_item(column, item, type, linked_to, button):
  with column:
    st.image(item['Image'], use_column_width='always')

    # use correct text on button
    if button == 'both':
      st.button(item['Title'] + ' - ' + item['Season+Episode'], key=random(), on_click=select_content, args=(item['Content_ID'], type, linked_to))
    elif pd.isna(item[button]):
      st.button(item['Season+Episode'], key=random(), on_click=select_content, args=(item['Content_ID'], type, linked_to))
    else:
      st.button(item[button], key=random(), on_click=select_content, args=(item['Content_ID'], type, linked_to))


def recommendations(df, type='unknown', linked_to=None, button='Title', len_rec=8):

  # check the number of items
  nbr_items = df.shape[0]

  if nbr_items != 0:    
    # create columns with the corresponding number of items
    columns = st.columns(len_rec)

    # convert df rows to dict lists
    items = df.to_dict(orient='records')

    # apply tile_item to each column-item tuple (created with python 'zip')
    any(tile_item(x[0], x[1], type, linked_to, button) for x in zip(columns, items))

def login(user):
  # loging and store activity
  st.session_state['user'] = user
  activity(activity='login')

def logout():
  # unload content if loaded
  unload_content()
  
  # make sure these are back to false
  st.session_state['open profile'] = False
  st.session_state['account create'] = False
  st.session_state['load search'] = False
  
  # store activity
  activity(activity='logout')

  # logout
  del st.session_state['user']

def select_content(show_id, type='unknown', linked_to=None):  
  # unload content if loaded
  unload_content()

  # load content and log
  st.session_state['index'] = show_id
  activity(activity='select content', id=show_id, attribute_link=type, attribute_value=linked_to)

def unload_content():
  # log unloading, and reset index
  if 'index' in st.session_state:
    activity(activity='unload content', id=st.session_state['index'])
    del st.session_state['index']

def rating_callback(id):
  # store the rating
  activity(activity='content rating', id=id, attribute_value=st.session_state.content_rating)
  calc.do_calculations()

def check_login():
  df_users = pd.read_csv('../data/users.csv', converters={"content_types": literal_eval}, dtype={'id': int})
  username = st.session_state.username
  password = st.session_state.password

  if not username or not password:
    st.warning('Please fill in both a username and password')

  # does the username exist
  elif username not in df_users['name'].unique():
    st.warning('Invalid username')

  # validate password
  elif password != df_users[df_users['name'] == username].iloc[0]['password']:
    st.warning('Invalid password')

  elif password == df_users[df_users['name'] == username].iloc[0]['password']:
    login(df_users[df_users['name'] == username].iloc[0])
    return

  login_page()

def login_page():
  st.title('Welcome to the BBC recommender system, please login')
  with st.form('login'):
    username = st.text_input('Username', key='username')
    password = st.text_input('Password', type='password', key='password')
    submit_button = st.form_submit_button("Login", on_click=check_login)

  button_press = st.button('No account? Create a new one!')
  if button_press:
    st.session_state['account create'] = True
  if st.session_state['account create']:
    create_account_form()

  st.stop()
    
def create_account_form():
  with st.form('new account'):
    username_input = st.text_input('Preferred username', key='new_username')
    password_input = st.text_input('Password', type='password', key='new_password')
    gender = st.selectbox('What is you gender?', ('Male', 'Female', 'Other'), key='new_gender')
    age = st.selectbox('What is you age', ('0-9', '10-17', '18-29', '30-49', '50-64', '65+', 'Prefer not to say'), index=2,  key='new_age')
    options = st.multiselect('What kind of content do you like?', pd.read_csv('../data/BBC_episodes.csv').Genre.unique(), key='content_types')
    submit_button = st.form_submit_button("Create account", on_click=create_account)

def create_account():
  users = pd.read_csv('../data/users.csv', converters={"content_types": literal_eval}, dtype={'id': int})
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

    activity(activity='create account', user_id=new_id)
    st.session_state['account create'] = False
    login(new_user.loc[0])
    calc.do_calculations()

def set_search():
  # make sure query is not empty
  if st.session_state.search == '':
    st.session_state['load search'] = False
    return

  unload_content()

  # set parameters
  st.session_state['load search'] = True
  st.session_state['search query'] = st.session_state.search
  activity(activity='search', attribute_value = st.session_state.search)
  # search is automatically loaded from app.py after this code

def stop_search():
  st.session_state['load search'] = False
  
def open_profile():
  st.session_state['open profile'] = True
  activity(activity='open profile')

def close_profile():
  st.session_state['open profile'] = False
  activity(activity='close profile')

def profile():
  col1, col2, col3, col4 = st.columns([1, 3, 3, 1])
  with col1:
    st.button('Go back', on_click=close_profile)
  with col4:
    st.button("Logout", key=random(), on_click=logout)
  genders = ['Male', 'Female', 'Other']
  agegroups = ['0-9', '10-17', '18-29', '30-49', '50-64', '65+', 'Prefer not to say']
  with st.form('new account'):
    username_input = st.text_input('Preferred username', key='new_username', disabled=True, value=st.session_state['user']['name'])
    password_input = st.text_input('Password', type='password', key='new_password', value=st.session_state['user']['password'])
    gender = st.selectbox('What is you gender?', genders, key='new_gender', index=genders.index(st.session_state['user']['gender']))
    age = st.selectbox('What is you age', agegroups, key='new_age', index=agegroups.index(st.session_state['user']['age']))
    options = st.multiselect('What kind of content do you like?', pd.read_csv('../data/BBC_episodes.csv').Genre.unique(), key='content_types', default=st.session_state['user']['content_types'])
    submit_button = st.form_submit_button("Change account", on_click=update_account)

  # download and delete personal data
  st.download_button(
    label="Download all personal data",
    data=chached_df(),
    file_name='personal_data.csv',
    mime='text/csv')
  st.button('Reset all content interactions', on_click=reset_interactions)
  st.button('Delete my account', on_click=delete_account)
  st.stop()

def update_account():
  # change session state
  st.session_state['user']['password'] = st.session_state.new_password
  st.session_state['user']['gender'] = st.session_state.new_gender
  st.session_state['user']['age'] = st.session_state.new_age
  st.session_state['user']['content_types'] = st.session_state.content_types
  
  # update user dataset
  users = pd.read_csv('../data/users.csv', converters={"content_types": literal_eval}, dtype={'id': int})
  users = users[users['id'] != st.session_state['user']['id']]
  users = pd.concat([users, st.session_state['user'].to_frame().T])
  users.to_csv('../data/users.csv', index=False)

  activity(activity='update account')

def chached_df():
  df = pd.read_csv('../data/activities.csv')
  df = df[df['user_id'] == st.session_state['user']['id']]
  return df.to_csv(index=False).encode('utf-8')

def reset_interactions():
  # delete all content interactions
  df = pd.read_csv('../data/activities.csv')
  df = df[~((df['user_id'] == st.session_state['user']['id']) & (~df['content_id'].isna()))]
  
  # store data and activity
  df.to_csv('../data/activities.csv', index=False)
  activity(activity='reset interactions')

def delete_account():
  user_id = st.session_state['user']['id']
  # log out
  logout()

  # delete account
  activity(activity='delete account', user_id=user_id)
  users = pd.read_csv('../data/users.csv', converters={"content_types": literal_eval}, dtype={'id': int})
  users = users[users['id'] != user_id]
  users.to_csv('../data/users.csv', index=False)

  #delete user data
  user_data = pd.read_csv('../data/activities.csv', converters={"content_types": literal_eval}, dtype={'id': int})
  user_data = user_data[user_data['user_id'] != user_id]
  user_data.to_csv('../data/activities.csv', index=False)

  #delete continue watching
  user_watch = pd.read_csv('../recommendations/next_episode.csv', converters={"content_types": literal_eval}, dtype={'id': int})
  user_watch = user_watch[user_watch['user_id'] != user_id]
  user_watch.to_csv('../recommendations/next_episode.csv', index=False)

def split_dataframe(df, chunk_size = 10000): 
    chunks = list()
    num_chunks = len(df) // chunk_size + 1
    for i in range(num_chunks):
        chunks.append(df[i*chunk_size:(i+1)*chunk_size])
    return chunks






def rating_prediction(ID):
    #read in activities and content dataframe
    df_act = pd.read_csv('../data/activities.csv')
    df_content = pd.read_csv('../data/BBC_episodes.csv')
    #set user_id equal to current user
    user_id = ID

    #Adds the show ID to the activities dataframe
    df_act = df_act.merge(df_content, left_on='content_id', right_on='Content_ID', how='left')[['Show_ID', 'content_id', 'activity', 'attribute_value', 'user_id', 'datetime']]


    ############################################################################################
    #TEMPORARY: based on ratings only

    #Filter out content rating
    df_ratings = df_act[df_act['activity'] == 'content rating']
    df_ratings['attribute_value'] = df_ratings['attribute_value'].astype(int)
    df_ratings = df_ratings.replace(to_replace=0,
                                    value=1)
    df_ratings = df_ratings.groupby(['Show_ID', 'user_id'], as_index=False).mean()

    if len(df_ratings[df_ratings['user_id']==user_id]) == 0:
      return(pd.DataFrame)


    df = df_ratings.pivot(index='user_id', columns='Show_ID', values='attribute_value').fillna(0)

    #TEMP: based on ratings only
    ############################################################################################



    #pick the nearest neighbours per point
    knn = NearestNeighbors(metric='cosine', algorithm='brute')
    knn.fit(df.values)
    distances, indices = knn.kneighbors(df.values, n_neighbors=3)

    neighbours = {}
    for i in range(0, len(indices)):
        nn = indices[i]
        dist = distances[i]
        e = nn[0]
        e_isbn = df.index[e]
        neighbours[e_isbn] = {"nn": [df.index[n] for n in nn[1:]], "dist": [1 - x for x in dist[1:]]}


    # Make a list of only the shows that exist in the dataset
    showlist = df.columns.tolist()

    #pick nearest neighbours for the specific user
    neigh = neighbours[user_id]
    nn = neigh['nn']
    dist = neigh['dist']

    ##calculate the predicted rating for all shows in the dataset (e.g. only shows that are arleady rated)
    ratinglist = []

    for show in showlist:
      numerator = 0
      denominator = 0

      for i in range(0, len(nn)):
        user = nn[i]
        user_rating = df.loc[user, show]

        numerator += user_rating * dist[i]
        denominator += dist[i]

      if denominator > 0:

        ratinglist.append(numerator / denominator)

      else:

        ratinglist.append(0)

    #make df of recommedations, return top 8

    df_recoms = pd.DataFrame(list(zip(showlist, ratinglist)),
                             columns=['Show_ID', 'Predicted_ratings'])
    df_recoms = df_recoms.sort_values(by='Predicted_ratings', ascending=False)
    df_recoms = df_recoms[df_recoms['Predicted_ratings'] > 4]

    return(df_recoms)
