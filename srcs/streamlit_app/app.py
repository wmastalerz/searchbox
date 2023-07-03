import os
import sys
import urllib.parse
import streamlit as st
from elasticsearch import Elasticsearch
sys.path.append('srcs')
from streamlit_app import utils, templates
from streamlit_app.pages import add_story, search
from ssl import create_default_context, CERT_NONE
from dotenv import load_dotenv

load_dotenv()
INDEX = os.environ['INDEX']
PAGE_SIZE = os.environ['PAGE_SIZE']
DOMAIN = os.environ['ESHOME']
PORT = os.environ['PORT']
DRIVER = os.environ['DRIVER']
username = os.environ['username']
password = os.environ['password']
ca_cert = os.environ['ca_cert'] 

context = create_default_context()
context.check_hostname = False        #temp workaround
context.verify_mode = CERT_NONE   #temp workaround

es = Elasticsearch(
    hosts=[{'host': DOMAIN, 'port': PORT}],
    http_auth=(username, password),
    scheme='https',
    ssl_context=context
)

utils.check_and_create_index(es, INDEX)

def set_session_state():
    """ """
    # default values
    if 'search' not in st.session_state:
        st.session_state.search = None
    if 'tags' not in st.session_state:
        st.session_state.tags = None
    if 'page' not in st.session_state:
        st.session_state.page = 1

    # get parameters in url
    para = st.experimental_get_query_params()
    if 'search' in para:
        st.experimental_set_query_params()
        st.session_state.search = urllib.parse.unquote(para['search'][0])
    if 'tags' in para:
        st.experimental_set_query_params()
        st.session_state.tags = para['tags'][0]
    if 'page' in para:
        st.experimental_set_query_params()
        st.session_state.page = int(para['page'][0])


def main():
    st.set_page_config(page_title='Search Engine')
    set_session_state()
    layout = st.sidebar.radio('', ['Search', 'Add docs'])
    st.write(templates.load_css(), unsafe_allow_html=True)
    # switch between pages
    if layout == 'Search':
        search.app()
    elif layout == 'Add docs':
        add_story.app()


if __name__ == '__main__':
    main()
