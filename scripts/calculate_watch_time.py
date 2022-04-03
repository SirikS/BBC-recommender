import pandas as pd

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