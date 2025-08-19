import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound, APIError

# 스키마 정의
REQUIRED_COLS = ["Genre", "Title", "Artist (Composer)", "Collaborators", "Orchestra", "Location", "Year"]
RENAME_MAP = {"Artist": "Artist (Composer)", "Collaborator": "Collaborators"}

# 유틸 함수들
def normalize_schema(df: pd.DataFrame) -> pd.DataFrame:
    for old, new in RENAME_MAP.items():
        if old in df.columns and new not in df.columns:
            df = df.rename(columns={old: new})
    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = ""
    tail = [c for c in df.columns if c not in REQUIRED_COLS]
    df = df[REQUIRED_COLS + tail]
    return df.fillna("")

def build_client_and_sheet():
    sa = st.secrets["gcp_service_account"]
    sheet_id = st.secrets["gsheets"]["spreadsheet_id"]
    ws_name = st.secrets["gsheets"]["worksheet"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(sa, scopes=scopes)
    client = gspread.authorize(creds)
    sh = client.open_by_key(sheet_id)
    ws = sh.worksheet(ws_name)
    return client, sh, ws

def load_data() -> pd.DataFrame:
    _, __, ws = build_client_and_sheet()
    rows = ws.get_all_records()
    return normalize_schema(pd.DataFrame(rows) if rows else pd.DataFrame(columns=REQUIRED_COLS))

def save_data(df: pd.DataFrame):
    _, __, ws = build_client_and_sheet()
    df = normalize_schema(df)
    ws.clear()
    ws.update([df.columns.tolist()] + df.astype(str).values.tolist())

# 앱 시작
st.title("💿 My LP Collection")

with st.sidebar.expander("🔎 연결 진단"):
    try:
        st.write("project_id:", st.secrets["gcp_service_account"]["project_id"])
        st.write("client_email:", st.secrets["gcp_service_account"]["client_email"])
        st.write("sheet_id:", st.secrets["gsheets"]["spreadsheet_id"])
        st.write("worksheet:", st.secrets["gsheets"]["worksheet"])
        if st.button("연결 점검 실행"):
            client, sh, ws = build_client_and_sheet()
            st.success("✅ Google Sheets 연결 OK")
            st.write("스프레드시트 제목:", sh.title)
            st.write("워크시트:", ws.title, "/ 행 수:", len(ws.get_all_values()))
    except Exception as e:
        st.error("❌ 연결 오류")
        st.code(str(e))

menu = st.sidebar.radio("메뉴 선택", ["추가하기", "검색하기", "전체보기", "수정/삭제"])

# 데이터 로드 및 예외 처리
try:
    df = load_data()
except SpreadsheetNotFound:
    st.error("❌ SpreadsheetNotFound: ID 오류 또는 공유 권한 확인")
    st.stop()
except WorksheetNotFound:
    st.error("❌ WorksheetNotFound: 시트 탭 이름 오류")
    st.stop()
except APIError as e:
    st.error("❌ APIError")
    st.code(str(e))
    st.stop()
except PermissionError as e:
    st.error("❌ PermissionError: 접근 권한 문제")
    st.code(str(e))
    st.stop()
except Exception as e:
    st.error("❌ 알 수 없는 오류")
    st.code(str(e))
    st.stop()

# ----------------- 분기 처리 -----------------
if menu == "추가하기":
    st.header("LP 추가하기")
    col1, col2 = st.columns(2)
    with col1:
        genre = st.text_input("Genre")
        title = st.text_input("Title")
        artist_comp = st.text_input("Artist (Composer)")
        collaborators = st.text_input("Collaborators")
    with col2:
        orchestra = st.text_input("Orchestra")
        location = st.text_input("Location")
        year = st.text_input("Year")
    if st.button("추가"):
        new_row = pd.DataFrame([{
            "Genre": genre.strip(), "Title": title.strip(),
            "Artist (Composer)": artist_comp.strip(),
            "Collaborators": collaborators.strip(),
            "Orchestra": orchestra.strip(),
            "Location": location.strip(),
            "Year": str(year).strip(),
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.success("✅ 저장 완료!")
        st.experimental_rerun()

elif menu == "검색하기":
    st.header("LP 검색하기")
    q = st.text_input("검색어 (모든 컬럼 대상)")
    if q:
        ql = q.lower()
        results = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(ql).any(), axis=1)]
        st.dataframe(results if not results.empty else pd.DataFrame(columns=df.columns))

elif menu == "전체보기":
    st.header("내 LP 전체 목록")
    view = df[REQUIRED_COLS] if set(REQUIRED_COLS).issubset(df.columns) else df
    st.dataframe(view)

elif menu == "수정/삭제":
    st.header("LP 수정 / 삭제")
    if df.empty:
        st.info("등록된 LP가 없습니다.")
    else:
        idx = st.selectbox("수정/삭제할 항목 선택",
                            options=df.index,
                            format_func=lambda i: f"{i}: {df.loc[i,'Title']} - {df.loc[i,'Artist (Composer)']}")
        row = df.loc[idx]
        col1, col2 = st.columns(2)
        with col1:
            e_genre = st.text_input("Genre", value=row["Genre"], key="e_genre")
            e_title = st.text_input("Title", value=row["Title"], key="e_title")
            e_artist = st.text_input("Artist (Composer)", value=row["Artist (Composer)"], key="e_artist")
            e_collab = st.text_input("Collaborators", value=row["Collaborators"], key="e_collab")
        with col2:
            e_orch = st.text_input("Orchestra", value=row["Orchestra"], key="e_orch")
            e_loc = st.text_input("Location", value=row["Location"], key="e_loc")
            e_year = st.text_input("Year", value=str(row["Year"]), key="e_year")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 수정 저장"):
                df.loc[idx, REQUIRED_COLS] = [e_genre, e_title, e_artist, e_collab, e_orch, e_loc, e_year]
                save_data(df)
                st.success("✅ 수정 완료!")
                st.experimental_rerun()
        with c2:
            if st.button("🗑️ 삭제"):
                df = df.drop(idx).reset_index(drop=True)
                save_data(df)
                st.success("❌ 삭제 완료!")
                st.experimental_rerun()
