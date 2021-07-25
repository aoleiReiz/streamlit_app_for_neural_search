import os

import requests
import streamlit as st
import streamlit.components.v1 as components
import altair as alt
import pandas as pd
from dotenv import load_dotenv


load_dotenv()

# side bar
AI_FUNCTIONALITY = ["Neural Search"]
st.sidebar.subheader("AI Functionality")
ai_function = st.sidebar.radio("", AI_FUNCTIONALITY)

st.sidebar.subheader("Retriever")
RETRIEVERS = ["DPR", "BM25"]
retriever = st.sidebar.radio("", RETRIEVERS)




# main page
query = st.text_input("Query")

if query:
    query_data = {
        "retriever": retriever,
        "data": [query]
    }
    if ai_function == AI_FUNCTIONALITY[0]:
        URL = os.environ["SERVER_ENDPOINT"]
        result = requests.post(URL, json=query_data).json()
        if result["Status"] == 0:
            documents = result["data"]
            df = pd.DataFrame(documents)
            df["file_id"] = df["file_id"].astype(int)

            st.subheader("Detail data")
            st.write(df[["file_id", "sentence", "score", "type"]])

            st.subheader("Analysis")
            st.markdown("**Top K Documents**")
            group_df = df.groupby("file_id")["score"].sum().reset_index().sort_values("score", ascending=False)

            c = alt.Chart(group_df).mark_bar().encode(
                x = alt.X("file_id:N", sort="-y"),
                y = alt.Y("score:Q"),
                color = alt.Color("score:Q")
            ).transform_window(
                rank='rank(score)',
                sort=[alt.SortField('score', order='descending')]
            ).transform_filter(
                (alt.datum.rank < 20)
            )
            st.altair_chart(c, use_container_width=True)

            selected_file_id = st.selectbox("Select file_id to Analyze Sentence", options=group_df["file_id"].tolist())
            if selected_file_id:
                rows = df[df.file_id == selected_file_id].iloc[0]["raw_sentences"]
                sentences_df = pd.DataFrame(rows, columns=["sentence", "type", "file_id"])
                sentences_df["file_id"] = sentences_df["file_id"].astype(int)
                sentences_df = sentences_df.merge(df[["sentence","score","file_id"]], how="left", on=["file_id","sentence"]).drop_duplicates()
                sentences_df["score"].fillna(0, inplace=True)
                st.write(sentences_df)

                in_abs = False
                in_content = False
                group_by_type = sentences_df.groupby("type")

                d = {}
                for _type, group in group_by_type:
                    if _type not in d:
                        d[_type] = []
                    for _, row in group.iterrows():
                        text = row["sentence"].strip("\n")
                        if 0 < row["score"] < 0.2:
                            text = f"<span class='card score1' style='color: white; background-color: #F4F269; padding: 4px;'>{text}</span>"
                        elif 0.2 <= row["score"] < 0.4:
                            text = f"<span class='card score2'  style='color: white; background-color: #CEE26B; padding: 4px;'>{text}</span>"
                        elif 0.4 <= row["score"] < 0.6:
                            text = f"<span class='card score3' style='color: white; background-color: #A8D26D; padding: 4px;'>{text}</span>"
                        elif 0.6 <= row["score"] < 0.8:
                            text = f"<span class='card score4' style='color: white; background-color: #82C26E; padding: 4px;'>{text}</span>"
                        elif 0.8 <= row["score"]:
                            text = f"<span class='card score5' style='color: white; background-color: #5Cb270; padding: 4px;'>{text}</span>"
                        else:
                            text = f"<span class='card' style='color: white;  padding: 4px;'>{text}</span>"
                        d[_type].append(text)
                st.subheader('Title')
                components.html("".join(d["Title"]))
                st.subheader('Abstract Description')
                components.html("<br/>".join(d["Abstract Description"]), scrolling=True)
                st.subheader('Content')
                components.html("<br/>".join(d["Content"]), scrolling=True, height=300)