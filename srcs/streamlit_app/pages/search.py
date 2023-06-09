import os
import sys
import streamlit as st
from elasticsearch import Elasticsearch
sys.path.append('srcs')
from streamlit_app import utils, templates
from ssl import create_default_context, CERT_NONE
from dotenv import load_dotenv

def app():
    """ search layout """
    load_dotenv()
    index = os.environ['INDEX']
    PAGE_SIZE = os.environ['PAGE_SIZE']
    DOMAIN = os.environ['ESHOME']
    PORT = os.environ['PORT']
    DRIVER = os.environ['DRIVER']
    username = os.environ['username']
    password = os.environ['password']
    ca_cert = os.environ['ca_cert'] 
    page_size = os.environ['PAGE_SIZE']
    context = create_default_context()
    context.check_hostname = False    #auth workaround
    context.verify_mode = CERT_NONE   #auth workaround

    es = Elasticsearch(
        hosts=[{'host': DOMAIN, 'port': PORT}],
        http_auth=(username, password),
        scheme='https',
        ssl_context=context
    )
    st.title('Search Resources')
    if st.session_state.search is None:
        search = st.text_input('Enter search words:')
    else:
        search = st.text_input('Enter search words:', st.session_state.search)

    if search:
        # reset tags when receive new search words
        if search != st.session_state.search:
            st.session_state.tags = None
        # reset search word
        st.session_state.search = None
        from_i = (st.session_state.page - 1) * page_size
        results = utils.index_search(es, index, search, st.session_state.tags,
                                     from_i, page_size)
        total_hits = results['aggregations']['match_count']['value']
        if total_hits > 0:
            # show number of results and time taken
            st.write(templates.number_of_results(total_hits, results['took'] / 1000),
                     unsafe_allow_html=True)
            # show popular tags
            if st.session_state.tags is not None and st.session_state.tags not in results['sorted_tags']:
                popular_tags = [st.session_state.tags] + results['sorted_tags']
            else:
                popular_tags = results['sorted_tags']

            popular_tags_html = templates.tag_boxes(search,
                                                    popular_tags[:10],
                                                    st.session_state.tags)
            st.write(popular_tags_html, unsafe_allow_html=True)
            # search results
            for i in range(len(results['hits']['hits'])):
                res = utils.simplify_es_result(results['hits']['hits'][i])
                st.write(templates.search_result(i + from_i, **res),
                         unsafe_allow_html=True)
                # render tags
                tags_html = templates.tag_boxes(search, res['tags'],
                                                st.session_state.tags)
                st.write(tags_html, unsafe_allow_html=True)

            # pagination
            if total_hits > page_size:
                total_pages = (total_hits + page_size - 1) // page_size
                pagination_html = templates.pagination(total_pages,
                                                       search,
                                                       st.session_state.page,
                                                       st.session_state.tags,)
                st.write(pagination_html, unsafe_allow_html=True)
        else:
            # no result found
            st.write(templates.no_result_html(), unsafe_allow_html=True)
