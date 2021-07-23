import requests
import streamlit as st
import streamlit.components.v1 as components

# side bar
AI_FUNCTIONALITY = ["Question and Answering", "Neural Search"]
st.sidebar.subheader("AI Functionality")
ai_function = st.sidebar.radio("", AI_FUNCTIONALITY)

st.sidebar.subheader("Retriever")
RETRIEVERS = ["DPR", "BM25"]
retriever = st.sidebar.radio("", RETRIEVERS)

st.sidebar.subheader("Searching Parameter")
RE_RETRIEVER_RANGE = list(range(20, 520, 20))
top_k_retriever = st.sidebar.select_slider("Top K Retriever", options=RE_RETRIEVER_RANGE)

RANKER_RANGE = list(range(5, 105, 5))
top_k_ranker = st.sidebar.select_slider("Top K Ranker", options=RANKER_RANGE)

FILTERS = ["All", "Title", "Abstract Description", "content"]
filters = st.sidebar.selectbox("Filters", FILTERS)

# main page
query = st.text_input("Query")

if query:
    query_data = {
        "top_k_retriever": top_k_retriever,
        "top_k_ranker": top_k_ranker,
        "retriever": retriever,
        "filters": filters,
        "re-rank": "yes",
        "data": [query]
    }
    if ai_function == AI_FUNCTIONALITY[0]:
        # question and answering
        URL = "http://localhost:5000/api/qa"
        result = requests.post(URL, json=query_data).json()
        if result["Status"] == 0:
            answers = result["data"]
            for answer in answers:
                html = """ 
                <div class="card" style="color: white;">
                    <div>
                        <b>Title</b>: {title}<br>
                        <b>score</b>: {score}
                    </div>
                    <p>
                    {content_prev}
                    <span style="font-weight: bold; background-color: deepskyblue;padding: 4px;">{answer}<span style="color: lightgreen">&nbsp&nbspAnswer </span></span>
                    {content_after}
                    </p>
                </div>
                """.format(content_prev=answer["context"][:answer["offset_start"]],
                           answer=answer["context"][answer["offset_start"]:answer["offset_end"]],
                           content_after=answer["context"][answer["offset_end"]:],
                           title=answer["title"], score=round(answer["score"],3)
                           )
                components.html(html)
                st.markdown("***")

    else:
        URL = "http://localhost:5000/api/search"
        result = requests.post(URL, json=query_data).json()
        if result["Status"] == 0:
            documents = result["data"]
            for doc in documents:
                with st.beta_container():
                  md = """ 
                        **Title**: {title}  
                        **score**: {score}  
                        **type**: {type}  
                        """.format(
                            type=doc["type"],
                            title=doc["title"],
                            score=round(doc["score"],3),
                        )
                  st.markdown(md)
                  st.write(doc["text"])
                st.markdown("***")
