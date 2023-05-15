import streamlit as st
import pandas as pd
d = {'col1': [1, 2], 'col2': [3, 4]}
df = pd.DataFrame(data=d)
fname=''
f_out = st.text_input(label='Output File Name: ',  value=fname)
print(f_out)
@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(sep=';').encode('utf-8')

csv = convert_df(df)

st.download_button(label="Save the Results in a CSV File",  data=csv,  file_name=f_out,  mime='text/csv')
