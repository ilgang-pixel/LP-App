import streamlit as st
import pandas as pd

# LP 데이터를 저장할 CSV 파일
DATA_FILE = "lp_collection.csv"

# CSV 불러오기
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Title", "Artist", "Year", "Genre"])

# CSV 저장하기
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.title("💿 My LP Collection")

menu = st.sidebar.radio("메뉴 선택", ["추가하기", "검색하기", "전체보기"])

df = load_data()

if menu == "추가하기":
    st.header("LP 추가하기")
    title = st.text_input("앨범 제목")
    artist = st.text_input("아티스트")
    year = st.text_input("발매 연도")
    genre = st.text_input("장르")

    if st.button("추가"):
        new_row = {"Title": title, "Artist": artist, "Year": year, "Genre": genre}
        df = df.append(new_row, ignore_index=True)
        save_data(df)
        st.success("✅ LP 추가 완료!")

elif menu == "검색하기":
    st.header("LP 검색하기")
    query = st.text_input("검색어 입력 (제목, 아티스트, 장르)")
    if query:
        results = df[df.apply(lambda row: query.lower() in row.astype(str).str.lower().to_string(), axis=1)]
        st.dataframe(results)

elif menu == "전체보기":
    st.header("내 LP 전체 목록")
    st.dataframe(df)

