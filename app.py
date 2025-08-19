import streamlit as st
import pandas as pd
import os

DATA_FILE = "lp_collection.csv"
REQUIRED_COLS = ["Title", "Artist", "Year", "Genre", "Collaborators", "Orchestra", "Location"]

def load_data():
    # CSV 없으면 빈 DF 생성
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=REQUIRED_COLS)

    df = pd.read_csv(DATA_FILE)

    # 누락 컬럼 자동 추가
    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = ""

    # 여분 컬럼은 유지하되, 표시/저장은 표준 순서 우선
    df = df[[*REQUIRED_COLS, *[c for c in df.columns if c not in REQUIRED_COLS]]]
    return df

def save_data(df: pd.DataFrame):
    # 저장 시 최소한 표준 컬럼은 보장
    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = ""
    df.to_csv(DATA_FILE, index=False)

st.title("💿 My LP Collection")
menu = st.sidebar.radio("메뉴 선택", ["추가하기", "검색하기", "전체보기", "수정/삭제"])

df = load_data()

# --------------- 추가하기 ---------------
if menu == "추가하기":
    st.header("LP 추가하기")
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("앨범 제목 (Title)")
        artist = st.text_input("아티스트 (Artist)")
        year = st.text_input("발매 연도 (Year)")
        genre = st.text_input("장르 (Genre)")
    with col2:
        collaborators = st.text_input("협연자 (Collaborators)")
        orchestra = st.text_input("오케스트라 (Orchestra)")
        location = st.text_input("위치 (Location)")

    if st.button("추가"):
        new_row = {
            "Title": title.strip(),
            "Artist": artist.strip(),
            "Year": str(year).strip(),
            "Genre": genre.strip(),
            "Collaborators": collaborators.strip(),
            "Orchestra": orchestra.strip(),
            "Location": location.strip(),
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        st.success("✅ LP 추가 완료!")

# --------------- 검색하기 ---------------
elif menu == "검색하기":
    st.header("LP 검색하기")
    query = st.text_input("검색어 (제목/아티스트/장르/협연자/오케스트라/위치)")
    if query:
        q = query.lower()
        results = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(q).any(), axis=1)]
        st.dataframe(results if not results.empty else pd.DataFrame(columns=df.columns))

# --------------- 전체보기 ---------------
elif menu == "전체보기":
    st.header("내 LP 전체 목록")
    st.dataframe(df)

# --------------- 수정 / 삭제 ---------------
elif menu == "수정/삭제":
    st.header("LP 수정 / 삭제")
    if df.empty:
        st.info("등록된 LP가 없습니다.")
    else:
        idx = st.selectbox("수정/삭제할 항목 선택", options=df.index, format_func=lambda i: f"{i}: {df.loc[i, 'Title']} - {df.loc[i, 'Artist']}")
        row = df.loc[idx]

        col1, col2 = st.columns(2)
        with col1:
            e_title = st.text_input("앨범 제목", value=row["Title"], key="e_title")
            e_artist = st.text_input("아티스트", value=row["Artist"], key="e_artist")
            e_year = st.text_input("발매 연도", value=str(row["Year"]), key="e_year")
            e_genre = st.text_input("장르", value=row["Genre"], key="e_genre")
        with col2:
            e_collab = st.text_input("협연자", value=row["Collaborators"], key="e_collab")
            e_orch = st.text_input("오케스트라", value=row["Orchestra"], key="e_orch")
            e_loc = st.text_input("위치", value=row["Location"], key="e_loc")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 수정 저장"):
                df.loc[idx, REQUIRED_COLS] = [e_title, e_artist, e_year, e_genre, e_collab, e_orch, e_loc]
                save_data(df)
                st.success("✅ 수정 완료!")
        with c2:
            if st.button("🗑️ 삭제"):
                df = df.drop(idx).reset_index(drop=True)
                save_data(df)
                st.success("❌ 삭제 완료!")
