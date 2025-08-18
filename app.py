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

menu = st.sidebar.radio("메뉴 선택", ["추가하기", "검색하기", "전체보기", "수정하기"])

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
    st.dataframe(df, use_container_width=True)

# ----------------- LP 수정 -----------------
elif menu == "수정하기":
    st.header("LP 수정하기")
    
    # 수정할 LP 선택
    lp_titles = df["Title"].tolist()
    lp_to_edit = st.selectbox("수정할 LP 선택", lp_titles)

    # 선택된 LP 데이터 로드
    if lp_to_edit:
        selected_lp = df[df["Title"] == lp_to_edit].iloc[0]
        
        # 수정할 값 입력 폼
        title = st.text_input("앨범 제목", value=selected_lp["Title"])
        artist = st.text_input("아티스트", value=selected_lp["Artist"])
        year = st.text_input("발매 연도", value=selected_lp["Year"])
        genre = st.text_input("장르", value=selected_lp["Genre"])
        collaborators = st.text_input("협연자", value=selected_lp["Collaborators"])
        orchestra = st.text_input("오케스트라", value=selected_lp["Orchestra"])
        location = st.text_input("위치", value=selected_lp["location"])

        if st.button("수정"):
            # 수정된 데이터 업데이트
            df.loc[df["Title"] == lp_to_edit, "Title"] = title
            df.loc[df["Title"] == lp_to_edit, "Artist"] = artist
            df.loc[df["Title"] == lp_to_edit, "Year"] = year
            df.loc[df["Title"] == lp_to_edit, "Genre"] = genre
            df.loc[df["Title"] == lp_to_edit, "Collaborators"] = collaborators
            df.loc[df["Title"] == lp_to_edit, "Orchestra"] = orchestra
            df.loc[df["Title"] == lp_to_edit, "location"] = location

            save_data(df)
            st.success("✅ LP 수정 완료!")
