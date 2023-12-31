# -*- coding: utf-8 -*-
"""Get_pull_data.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1All63qg_Hy_NjRGjZx8iJAA4_SrV8__A
"""

pip install PyGithub

pip install XlsxWriter

# Libraries
import pandas as pd
from github import Github
import xlsxwriter

# The data of the repository
owner = 'awslabs'
repo = 'git-secrets'

# Empty dataframe
df_pulls = pd.DataFrame()

g = Github()

# 'User'/'Repository'
repo = g.get_repo(f'{owner}/{repo}')
pulls = repo.get_pulls()
for pull in pulls:
  try:
    loc_df = pd.DataFrame({'author':str(pull.user.login),
                           'pull_date':pull.created_at,
                           'body':pull.body,
                           'review_comment_url':pull.review_comment_url,
                           'title':pull.title
                           }, index=[0])
  except:
    loc_df = pd.DataFrame({'author':None,
                           'pull_date':None,
                           'body':None,
                           'review_comment_url':None,
                           'title':None
                           }, index=[0])

  df_pulls = pd.concat([df_pulls, loc_df], ignore_index=True)
df_pulls = df_pulls.sort_values('pull_date')

# Count of actions performed by each user by all the time
if len(df_pulls) != 0:
  df_count_pulls_groupby = df_pulls.groupby('author').agg({'pull_date':'count'}).rename(columns={'pull_date':'pull_count'}).reset_index().sort_values('pull_count', ascending=False)

# Count of actions performed by each user per date
if len(df_pulls) != 0:
  df_pulls['date'] = df_pulls['pull_date'].dt.date
  df_pulls_count = df_pulls.groupby(['author', 'date']).agg({'pull_date':'count'}).rename(columns={'pull_date':'pull_count'}).reset_index().sort_values('date')

# Mean time per user
result_data_pulls = []

# Unique authors
authors = df_pulls['author'].unique()

for author in authors:
    author_data = df_pulls[df_pulls['author'] == author]
    author_data = author_data.sort_values('pull_date')
    author_data['delta'] = author_data['pull_date'].diff().fillna(pd.Timedelta(seconds=0))
    average_delta = author_data['delta'].mean()
    result_data_pulls.append(pd.Series({'author': author, 'average_delta': average_delta}))

result_df_pulls = pd.concat(result_data_pulls, axis=1).T
result_df_pulls = result_df_pulls.reset_index(drop=True)

result_df_pulls['delta_seconds'] = result_df_pulls['average_delta'].dt.total_seconds()
mean_delta_per_user = result_df_pulls[result_df_pulls['delta_seconds'] > 0][['author', 'average_delta']]
mean_delta_per_user = mean_delta_per_user.rename(columns={'average_delta':'average_delta_days'}).sort_values('average_delta_days', ascending=False)

# Writing to Excel
writer = pd.ExcelWriter('Pull_Data.xlsx', engine='xlsxwriter')

df_pulls.to_excel(writer, sheet_name='All data', index = False)
df_count_pulls_groupby.to_excel(writer, sheet_name='Count pulls per user', index = False)
df_pulls_count.to_excel(writer, sheet_name='Count pulls per user by date', index = False)
mean_delta_per_user.to_excel(writer, sheet_name='Mean delta time', index = False)

writer.close()

