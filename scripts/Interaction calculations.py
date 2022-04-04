import pandas as pd

# create watchtime dataset
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
# load ratings
activities = pd.read_csv('../data/activities.csv')
ratings = activities[activities['activity'] == 'content rating']

# select most recent rating
ratings = ratings.sort_values('datetime', ascending=False).groupby(['content_id', 'user_id']).head(1)

# reformat and save
ratings = ratings[['user_id', 'content_id', 'attribute_value']].rename({'attribute_value':'rating'}, axis=1)
ratings.to_csv('../data/ratings.csv', index=False)