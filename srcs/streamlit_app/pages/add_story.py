import os
import sys
import json
import streamlit as st
from elasticsearch import Elasticsearch
sys.path.append('srcs')
from streamlit_app import utils, templates


def app():
    """ page for adding document """
    index = os.environ['INDEX']
    domain = os.environ['DOMAIN']
    driver = os.environ['DRIVER']
    es = Elasticsearch(host=domain)
    st.title('Add docs')
    st.write(templates.info_add_story(), unsafe_allow_html=True)
    with st.expander('By URL'):
        st.write(templates.info_add_url(), unsafe_allow_html=True)
        url = st.text_input('Enter page docs or list url:')
        url_type = st.radio('Url type:', ['story', 'list'])
        add_story_url = st.button('Add', 'submit_add_story_url')

    with st.expander('By docx, pdf, xlsx, pptx'):
        st.write('File containing stories')
        raw_file = st.file_uploader('Upload a .docx, .pdf, .xlsx, .pptx file', ['docx', 'pdf', 'xlsx', 'pptx'])
        add_story_raw = st.button('Add', 'submit_add_raw_file')

    if add_story_url:
        stories = {}
        
        if url_type == 'story':
            with st.spinner('Getting 1 doc content...'):
                stories[url] = utils.get_story_from_url(url, driver)
        
        else:
            
            story_urls = utils.get_story_urls_from_list(url, driver)
            for i, _url in enumerate(story_urls):
                with st.spinner(f'Getting {i + 1}/{len(story_urls)} doc content...'):
                    stories[_url] = utils.get_story_from_url(_url, driver)

        
        utils.index_stories(es, index, stories)

    if raw_file is not None and add_story_raw:
        data = raw_file.read()
        stories = json.loads(data)
        
        utils.index_stories(es, index, stories)

    
    
    
    
    
    
    
    
    
