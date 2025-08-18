import streamlit as st
import pandas as pd

# LP 데이터를 저장할 CSV 파일
DATA_FILE = "lp_collection.csv"

# CSV 불러오기
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Title", "Artist", "Year", "Genre", "Collaborators", "Orchestra", "location"
        ])

# CSV 저장하기
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.title("💿 My LP Collection")

menu = st.sidebar.radio("메뉴 선택", ["추가하기", "검색하기", "전체보기"])

df = load_data()

# ----------------- LP 추가 -----------------
if menu == "추가하기":
    st.header("LP 추가하기")
    title = st.text_input("앨범 제목")
    artist = st.text_input("아티스트")
    year = st.text_input("발매 연도")
    genre = st.text_input("장르")
    collaborators = st.text_input("협연자")
    orchestra = st.text_input("오케스트라")
    location = st.text_input("위치")

    if st.button("추가"):
        new_row = {
            "Title": title,
            "Artist": artist,
            "Year": year,
            "Genre": genre,
            "Collaborators": collaborators,
            "Orchestra": orchestra,
            "location": location
        }

        # append 대신 concat 사용
        new_row_df = pd.DataFrame([new_row])
        df = pd.concat([df, new_row_df], ignore_index=True)

        save_data(df)
        st.success("✅ LP 추가 완료!")

# ----------------- LP 검색 -----------------
elif menu == "검색하기":
    st.header("LP 검색하기")
    query = st.text_input("검색어 입력 (제목, 아티스트, 장르, 협연자, 오케스트라, 위치)")
    if query:
        # 모든 컬럼에서 검색어 포함 여부 확인
        results = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(query.lower()).any(), axis=1)]
        st.dataframe(results)

# ----------------- 전체보기 -----------------
elif menu == "전체보기":
    st.header("내 LP 전체 목록")
    st.dataframe(df)
