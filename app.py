import streamlit as st
import pandas as pd
import io

# ==========================================
# 1. 웹 사이트 제목 및 기본 세팅
# ==========================================
st.set_page_config(page_title="ZEB 최적화 플랫폼", layout="wide")
st.title("🏢 ZEB 5등급 자동 평가 & ROI 컨설팅 플랫폼")
st.markdown("BIM 기반 초기 설계 타당성 검토 시스템 (통합 완전판)")

# ==========================================
# 2. 가상의 엑셀 마스터 DB (단열재 & 창호)
# ==========================================
csv_insulation = """DB_ID,Category,Material,Thickness_mm,k_value,U_value_design,Price_per_sqm
INS_001,XPS,특호,100,0.027,0.270,8500
INS_002,EPS,2종1호,120,0.031,0.258,7200
INS_003,PIR,2종2호,80,0.020,0.250,10250
INS_004,PIR,2종2호,95,0.020,0.233,12170
INS_005,PF,일반형,140,0.018,0.128,28000
INS_006,PF,고성능형,190,0.018,0.094,38000"""

csv_window = """DB_ID,Type,Spec,U_value,SHGC,Price_per_sqm
WIN_001,일반복층,24T 일반 투명,2.800,0.70,55000
WIN_002,싱글로이,24T 싱글 로이,1.500,0.55,90000
WIN_003,더블로이,24T 더블 로이,1.200,0.28,120000
WIN_004,삼중로이,43T 삼중 로이,0.850,0.46,195000"""

# 텍스트 데이터를 표(DataFrame)로 변환
df_insulation = pd.read_csv(io.StringIO(csv_insulation))
df_window = pd.read_csv(io.StringIO(csv_window))

# ==========================================
# 3. 사용자 입력 UI (좌측 사이드바 패널)
# ==========================================
st.sidebar.header("🎯 1. ZEB 목표 설정")
energy_independence = st.sidebar.slider("예상 에너지 자립률 (%)", 0, 150, 25)

st.sidebar.markdown("---")
st.sidebar.header("📐 2. 건물 형태 정보 (BIM 파싱)")
total_wall_area = st.sidebar.number_input("전체 외벽 면적 (㎡)", min_value=100, value=5000, step=100)
wwr = st.sidebar.slider("창면적비 (WWR, %)", 10, 80, 40) 

st.sidebar.markdown("---")
st.sidebar.header("🧱 3. 불투명 외피 (단열재)")
# 법적 열관류율 최대/최소값 안전장치 적용 (0.050 ~ 1.000)
legal_u_wall = st.sidebar.number_input(
    "벽체 법적 열관류율 (W/㎡·K)", 
    min_value=0.050, 
    max_value=1.000, 
    value=0.240, 
    step=0.010, 
    format="%.3f"
)
selected_insulation = st.sidebar.selectbox("단열재 스펙 선택", df_insulation['Material'].tolist())

st.sidebar.markdown("---")
st.sidebar.header("🪟 4. 투명 외피 (창호)")
# 법적 열관류율 최대/최소값 안전장치 적용 (0.500 ~ 5.000)
legal_u_win = st.sidebar.number_input(
    "창호 법적 열관류율 (W/㎡·K)", 
    min_value=0.500, 
    max_value=5.000, 
    value=1.500, 
    step=0.100, 
    format="%.3f"
)
selected_window = st.sidebar.selectbox("창호 스펙 선택", df_window['Spec'].tolist())

# ==========================================
# 4. 연산 로직 처리 (백엔드 엔진)
# ==========================================
# 면적 분할 로직 (전체 면적을 창문과 단열 벽체로 나눔)
window_area = total_wall_area * (wwr / 100)
opaque_wall_area = total_wall_area - window_area

# 단열재 물성치 및 비용 계산
ins_data = df_insulation[df_insulation['Material'] == selected_insulation]
ins_u = ins_data['U_value_design'].values[0]
ins_price = ins_data['Price_per_sqm'].values[0]
ins_cost = opaque_wall_area * ins_price
ins_pass = ins_u <= legal_u_wall

# 창호 물성치 및 비용 계산
win_data = df_window[df_window['Spec'] == selected_window]
win_u = win_data['U_value'].values[0]
win_shgc = win_data['SHGC'].values[0]
win_price = win_data['Price_per_sqm'].values[0]
win_cost = window_area * win_price
win_pass = win_u <= legal_u_win

# 총 공사비 산출
total_envelope_cost = ins_cost + win_cost

# ZEB 등급 판정 기준
if energy_independence >= 120:
    zeb_grade, grade_color = "ZEB Plus", "🌈"
elif energy_independence >= 100:
    zeb_grade, grade_color = "ZEB 1등급", "🥇"
elif energy_independence >= 80:
    zeb_grade, grade_color = "ZEB 2등급", "🥈"
elif energy_independence >= 60:
    zeb_grade, grade_color = "ZEB 3등급", "🥉"
elif energy_independence >= 40:
    zeb_grade, grade_color = "ZEB 4등급", "🟢"
elif energy_independence >= 20:
    zeb_grade, grade_color = "ZEB 5등급", "🟡"
else:
    zeb_grade, grade_color = "등급 외 (인증 불가)", "❌"

# ==========================================
# 5. 결과 웹 화면 출력 (프론트엔드 UI)
# ==========================================

# [최상단] 핵심 KPI: ZEB 등급 판정 결과
st.subheader("🏆 종합 판정: ZEB 인증 예상 등급")
st.markdown(f"## {grade_color} **{zeb_grade}** (에너지 자립률: {energy_independence}%)")

if zeb_grade == "등급 외 (인증 불가)" or not ins_pass or not win_pass:
    st.error("🚨 **AI 컨설팅 경고:** 인증 요건(자립률 20% 이상 및 법적 열관류율)을 충족하지 못했습니다. 좌측 사이드바에서 자재 스펙이나 자립률을 상향 조정해 주세요.")
else:
    st.success("💡 **AI 컨설팅 제안:** 완벽합니다! 패시브 방어선과 신재생에너지 기준을 모두 충족했습니다.")

st.markdown("---")

# [중단] 공사비 요약 대시보드
st.subheader("💰 재무 분석: 외피(단열+창호) 총 자재비 예측")
st.markdown(f"### ₩ {total_envelope_cost:,.0f} 원")
st.caption(f"산출 근거: (단열재 면적 {opaque_wall_area:,.0f}㎡ × 단가) + (창호 면적 {window_area:,.0f}㎡ × 단가)")

st.markdown("---")

# [하단] 세부 스펙 분석 (단열재와 창호를 좌우로 나누어 비교)
col1, col2 = st.columns(2)

with col1:
    st.subheader("🧱 불투명 외피 (단열재) 성능")
    st.metric("적용 면적", f"{opaque_wall_area:,.0f} ㎡")
    st.metric("열관류율 (U-value)", f"{ins_u} W/㎡·K")
    if ins_pass:
        st.info(f"✅ 합격 (기준: {legal_u_wall:.3f} 이하)")
    else:
        st.error(f"❌ 불합격 (기준: {legal_u_wall:.3f} 이하)")

with col2:
    st.subheader("🪟 투명 외피 (창호) 성능")
    st.metric("적용 면적 (WWR 반영)", f"{window_area:,.0f} ㎡")
    st.metric("열관류율 / SHGC", f"U: {win_u} / SHGC: {win_shgc}")
    if win_pass:
        st.info(f"✅ 합격 (기준: {legal_u_win:.3f} 이하)")
    else:
        st.error(f"❌ 불합격 (기준: {legal_u_win:.3f} 이하)")
