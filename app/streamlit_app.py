import streamlit as st
import psycopg2
import polars as pl
import pandas as pd
from PIL import Image
from io import BytesIO
import requests


icon = Image.open("./icons/youtube_v2.png", mode="r")

st.set_page_config(
    page_title="YouTube RecoMaster",
    page_icon=icon,
    layout="centered",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()

@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()
        # return pl.read_database(query, cur)

title, logo = st.columns([4,2.91])
with title: 
    st.title("YouTube RecoMaster")
with logo: 
    st.write("")
    st.image(icon, width=70)
    
st.slider("Size")

video_name = st.text_input("Enter a video name")
st.write(f"You entered: {video_name}")

data = run_query(
    f"""
        SELECT DISTINCT 
            i.video_id,
            i.title, 
            i.channeltitle,
            i.thumbnail_link,
            l.link_video,
            v.categoryname,
            m.view_count 
        FROM gold.informationvideos i 
            INNER JOIN gold.linkvideos l 
                ON i.video_id  = l.video_id
            INNER JOIN gold.videocategory v 
                ON i.categoryid = v.categoryid 
            INNER JOIN (
                SELECT video_id, max(view_count) AS view_count 
                FROM gold.metricvideos
                GROUP BY video_id) AS m
                ON i.video_id = m.video_id
        WHERE i.title LIKE '%{video_name}%'
        LIMIT 10;
    """
)

videos = {
    "video_id": [e[0] for e in data],
    "title": [e[1] for e in data],
    "channeltitle": [e[2] for e in data],
    "thumbnail_link": [e[3] for e in data],
    "link_video": [e[4] for e in data],
    "categoryname": [e[5] for e in data],
    "view_count": [e[6] for e in data]
}

video_url = [
    "https://www.youtube.com/embed/J78aPJ3VyNs"
]                                   
recommended_videos = [
    "https://www.youtube.com/embed/UYXa8R9vvzA",
    "https://www.youtube.com/embed/02MaoZ5n-uM",
    "https://www.youtube.com/embed/ucDDYszgj5c",
    "https://www.youtube.com/embed/M9Pmf9AB4Mo",
    "https://www.youtube.com/embed/tkaU_Ctzhes",
]
recommended_videos += videos['link_video']

def display_video(url):
    if url not in recommended_videos:
        st.markdown(
            f'''<iframe width="705" height="460" src="{url}" title="YouTube video player" frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; 
                web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>''', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'''<iframe width="355" height="160" src="{url}" title="YouTube video player" frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; 
                web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>''', 
            unsafe_allow_html=True
        )

# st.video(video_url)
# display_video(video_url)
# st.write("")

st.subheader("Recommended Videos:")
for video_id,title,channeltitle,thumbnail_link,link_video,categoryname,view_count in zip(
    videos['video_id'],videos['title'],videos['channeltitle'],
    videos['thumbnail_link'],videos['link_video'],videos['categoryname'],videos['view_count']):
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # display_video(link_video)
        img = Image.open(BytesIO(requests.get(thumbnail_link).content))
        st.image(img)
    
    with col2:
        st.markdown(f"""
            <div style="line-height: 1.5;">
                <span style="font-weight: bold;">{title}</span><br>
                <span style="opacity: 0.6;">channel: {channeltitle}</span><br>
                <span style="opacity: 0.6;">category: {categoryname}</span><br>
                <span style="opacity: 0.6;">views: {view_count}</span>
            </div>
            """, unsafe_allow_html=True)

    st.write("---")
    



df = pl.DataFrame(data)
st.table(df)