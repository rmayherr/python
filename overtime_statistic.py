#!/usr/bin/env python
# coding: utf-8

# ## HUDBDC overtime analysis

# In[1]:


import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from glob import glob
from datetime import datetime as dt

#Suppress warning
pd.set_option('mode.chained_assignment', None)
# Read all xls files from desired place
files = glob(os.path.dirname(os.path.abspath(__file__)) + '/Excel/OT*.xls')
# Read first excel file into dataframe
df = pd.read_excel(files[0], header=7, keep_default_na=False,
                   usecols=range(2, 10), skip_blank_lines=True)
# Read further excel files and concatenate them together
for i in range(1, len(files)):
    df = pd.concat([df, pd.read_excel(files[i], header=7, keep_default_na=False,
                                      usecols=range(2, 10), skip_blank_lines=True)])
# Change column names
df.rename(columns={'List of people': 'Employees', 'Date of overtime': 'Date',
                   'Nr. of hours': 'Hours'}, inplace=True)
# Remove unnecessary both rows and columns
mask1 = df['Employees'] != ''
mask2 = df['Start'] != ''
df = df[mask1 & mask2]
# Set Date column as datetime object and Hours as float64
df['Date'] = pd.to_datetime(df['Date'])
df['Hours'] = df['Hours'].astype('float64')
# Summarize hours by employees
df_sum_ot = df.groupby(['Employees']).sum()['Hours'].to_frame().reset_index()
# Create figure
fig = px.bar(df_sum_ot.sort_values('Hours', ascending=False),
             x='Employees', y='Hours', text='Hours',
             title='Sum of requested overtime between ' + str(df['Date'].min()).split(' ')[0] + ' and ' +
             str(df['Date'].max()).split(' ')[0])
fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
#fig.show()
fig.write_html(sys.argv[0][:sys.argv[0].rfind('/')] + '/summary_overtime.html')

# In[2]:


#Change date value to month name
def month_name_column(row):
    return dt.strftime(row, '%B')

#Dictionary to map month names to month numbers
month_map = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5,
             'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10,
             'November': 11, 'December': 12}

#Create new column for month number
df['Month'] = df['Date'].apply(month_name_column)
#Group by Months
df_sum_hours = df.groupby(['Month']).agg({'Hours': 'sum'})
#Remove index
df_sum_hours.reset_index(inplace=True)
#Create new column for month numbers
df_sum_hours['Month number'] = df_sum_hours['Month'].map(month_map)
#Sort column
df_sum_hours.sort_values('Month number', inplace=True)
#Create chart
fig = go.Figure(go.Bar(
    y=df_sum_hours['Month'],
    x=df_sum_hours['Hours'],
    orientation='h',
    marker=dict(
        color='rgba(89, 200, 23, 0.6)',
        line=dict(color='rgba(89, 200, 23, 1.0)', width=3))
))
fig.update_layout(
    xaxis=dict(
        showgrid=False,
        showline=False,
        showticklabels=True,
        zeroline=False,
        domain=[0.15, 1]
    ),
    yaxis=dict(
        showgrid=False,
        showline=False,
        showticklabels=True,
        zeroline=False,
    ),
    barmode='stack',
    paper_bgcolor='rgb(248, 248, 255)',
    plot_bgcolor='rgb(248, 248, 255)',
    margin=dict(l=120, r=10, t=140, b=80),
    showlegend=False,
    title='Number of overtime by months'
)
#fig.show()
fig.write_html(sys.argv[0][:sys.argv[0].rfind('/')] + '/summary_by_month.html')

# In[3]:


#Group by Customer and calculate sum of hours
df_sum_customers = df.groupby(['Customer']).agg({'Hours' : 'sum'})
#Create chart
fig = px.pie(df_sum_customers, values='Hours', names=df_sum_customers.index, title='Spent hours by customers')
fig.show()


# In[37]:


df_abn = df[df['Customer'] == 'ABN-AMRO']
df_abn_final = df_abn.groupby(['Month', 'Employees']).agg({'Hours' : 'sum'})
df_abn_final = df_abn_final.reset_index()
df_abn_total_hours = df_abn.groupby('Month').agg({'Hours' : 'sum'})
df_abn_total_hours.reset_index(inplace=True)
df_result = pd.merge(df_abn_final, df_abn_total_hours, on='Month', suffixes=('', ' Total'))
df_result['Month Num'] = df_result['Month'].map(month_map)
df_result.sort_values('Month Num', inplace=True)
fig = px.bar(df_result,
             x="Month",
             y="Hours", hover_data=['Employees', 'Hours', 'Hours Total'], 
             color_continuous_scale=px.colors.sequential.Viridis,
             barmode='stack', color='Hours')
#fig.show()
fig.write_html(sys.argv[0][:sys.argv[0].rfind('/')] + '/summary_by_customer.html')

# In[ ]:





# In[ ]:




