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

    with st.expander('By JSON'):
        st.write('JSON file containing one or more stories with format:')
        st.write({
            '$STORY_URL': {
                'author': '$AUTHOR_NAME',
                'length': '$INT min read',
                'title': '$STORY_TITLE',
                'tags': ['$TAG-NAME', ],
                'content': ['$PARAGRAPH_TEXT', ]
            },
        })
        json_file = st.file_uploader('Upload a .json file', ['json'])
        add_story_json = st.button('Add', 'submit_add_story_json')

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

    if json_file is not None and add_story_json:
        data = json_file.read()
        stories = json.loads(data)
        
        utils.index_stories(es, index, stories)

    
    
    
    
    
    
    
    
    
