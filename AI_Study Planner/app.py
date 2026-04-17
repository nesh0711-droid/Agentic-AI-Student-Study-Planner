import streamlit as st
import pandas as pd
import datetime as _dt

# ── BACKEND IMPORTS — 
from modules.canvas_api import *
from modules.calendar_api import *
from modules.preprocessing import *
from modules.prediction import *
from modules.scheduling import *
from modules.risk_detection import *
from modules.reminder import generate_reminders
from modules.assistant import smart_assistant

def safe_df_for_assistant(df):
    
    import modules.assistant as _assistant
    from datetime import timedelta

    def _patched_get_due_this_week(df):
        due_col = pd.to_datetime(df['due_date'])
        if due_col.dt.tz is not None:
            due_col = due_col.dt.tz_localize(None)
        today    = pd.Timestamp.today().normalize()
        end_week = today + timedelta(days=7)
        upcoming = df[(due_col >= today) & (due_col <= end_week)]
        if upcoming.empty:
            return "No assignments due this week."
        result = "Assignments due this week:\n"
        for _, row in upcoming.iterrows():
            try:
                due_str = pd.to_datetime(row['due_date']).date()
            except:
                due_str = row['due_date']
            result += f"- {row['assignment_name']} (Due: {due_str})\n"
        return result

    _assistant.get_due_this_week = _patched_get_due_this_week
    return df

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agentic AI StudyPlanner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');

*,*::before,*::after{box-sizing:border-box;}
:root{
  --white:#ffffff; --bg:#f0f2f8; --bg2:#e8ebf4; --card:#ffffff;
  --border:#e1e5f0; --border2:#c8cedf;
  --indigo:#4f46e5; --indigo2:#6366f1; --ind-dim:rgba(79,70,229,0.08); --ind-mid:rgba(79,70,229,0.18);
  --teal:#0d9488; --teal-dim:rgba(13,148,136,0.08);
  --red:#dc2626; --red-dim:rgba(220,38,38,0.07);
  --orange:#ea580c; --org-dim:rgba(234,88,12,0.07);
  --green:#16a34a; --grn-dim:rgba(22,163,74,0.07);
  --text:#0f172a; --text2:#475569; --text3:#94a3b8; --text4:#cbd5e1;
  --ff:'Plus Jakarta Sans',sans-serif; --mono:'Fira Code',monospace;
  --r:12px; --r2:8px;
  --sh:0 1px 3px rgba(0,0,0,0.06),0 4px 16px rgba(0,0,0,0.04);
  --sh2:0 2px 8px rgba(0,0,0,0.08),0 8px 24px rgba(0,0,0,0.06);
}
html,body,[class*="css"],.stApp{font-family:var(--ff)!important;background:var(--bg)!important;color:var(--text)!important;}
[data-testid="stHeader"],[data-testid="stToolbar"],#MainMenu,footer,.stDeployButton{display:none!important;}
.block-container{padding:0!important;max-width:100%!important;}

[data-testid="stSidebar"]{background:var(--white)!important;border-right:1px solid var(--border)!important;min-width:220px!important;max-width:256px!important;box-shadow:2px 0 12px rgba(0,0,0,0.04)!important;}
[data-testid="stSidebar"]>div{padding:0!important;}
[data-testid="stSidebar"] *{font-family:var(--ff)!important;}
[data-testid="stSidebarNav"]{display:none!important;}
[data-testid="stSidebar"]::-webkit-scrollbar{width:3px;}
[data-testid="stSidebar"]::-webkit-scrollbar-thumb{background:var(--border2);border-radius:4px;}

.main .block-container{padding:28px 48px 28px 80px!important;max-width:100%!important;}
section.main > div.block-container{padding-left:80px!important;}
[data-testid="stMainBlockContainer"]{padding-left:80px!important;}

[data-testid="stTabs"] [role="tablist"]{background:transparent;border:none;padding:0;gap:4px;border-bottom:2px solid var(--border);margin-bottom:0;}
[data-testid="stTabs"] button[role="tab"]{font-family:var(--ff)!important;font-size:13px!important;font-weight:600!important;color:var(--text3)!important;background:transparent!important;border:none!important;border-radius:0!important;padding:10px 20px!important;border-bottom:2px solid transparent!important;margin-bottom:-2px!important;transition:all .15s;letter-spacing:0;text-transform:none;}
[data-testid="stTabs"] button[role="tab"]:hover{color:var(--text2)!important;background:var(--ind-dim)!important;border-radius:8px 8px 0 0!important;}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{color:var(--indigo)!important;background:transparent!important;border-bottom:2px solid var(--indigo)!important;}
[data-testid="stTabsContent"]{background:transparent!important;border:none!important;padding:24px 0 0!important;}

[data-testid="metric-container"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--r)!important;padding:20px 22px!important;box-shadow:var(--sh)!important;}
[data-testid="stMetricLabel"]{font-family:var(--ff)!important;font-size:12px!important;font-weight:600!important;color:var(--text3)!important;letter-spacing:.01em!important;text-transform:none!important;}
[data-testid="stMetricValue"]{font-family:var(--ff)!important;font-size:32px!important;font-weight:800!important;color:var(--text)!important;line-height:1.1!important;}
[data-testid="stMetricDelta"]{display:none!important;}

.stButton>button{font-family:var(--ff)!important;font-size:13px!important;font-weight:600!important;background:var(--white)!important;border:1px solid var(--border2)!important;color:var(--text2)!important;border-radius:var(--r2)!important;padding:8px 16px!important;transition:all .15s!important;letter-spacing:0!important;text-transform:none!important;box-shadow:0 1px 2px rgba(0,0,0,0.05)!important;}
.stButton>button:hover{border-color:var(--indigo2)!important;color:var(--indigo)!important;background:var(--ind-dim)!important;}
.btn-primary .stButton>button{background:var(--indigo)!important;color:white!important;border:none!important;font-size:14px!important;padding:12px 28px!important;border-radius:10px!important;box-shadow:0 4px 14px rgba(79,70,229,0.3)!important;}
.btn-primary .stButton>button:hover{background:var(--indigo2)!important;color:white!important;box-shadow:0 6px 20px rgba(79,70,229,0.4)!important;transform:translateY(-1px)!important;}
.btn-teal .stButton>button{background:var(--teal)!important;color:white!important;border:none!important;border-radius:var(--r2)!important;box-shadow:0 2px 8px rgba(13,148,136,0.25)!important;}
.btn-teal .stButton>button:hover{background:#0f766e!important;color:white!important;}
.btn-cal .stButton>button{background:var(--ind-dim)!important;color:var(--indigo)!important;border:1px solid var(--ind-mid)!important;border-radius:6px!important;font-size:11px!important;padding:4px 10px!important;box-shadow:none!important;font-weight:600!important;}
.btn-cal .stButton>button:hover{background:var(--indigo)!important;color:white!important;border-color:var(--indigo)!important;}
.qbtn .stButton>button{width:100%!important;text-align:left!important;background:var(--card)!important;border:1px solid var(--border)!important;color:var(--text2)!important;border-radius:10px!important;padding:10px 14px!important;font-size:13px!important;box-shadow:var(--sh)!important;}
.qbtn .stButton>button:hover{border-color:var(--indigo2)!important;color:var(--indigo)!important;background:var(--ind-dim)!important;}

[data-testid="stSelectbox"]>div>div{background:var(--white)!important;border:1px solid var(--border2)!important;border-radius:var(--r2)!important;color:var(--text)!important;font-family:var(--ff)!important;font-size:13px!important;}
.stTextInput input{background:var(--white)!important;border:1px solid var(--border2)!important;border-radius:var(--r2)!important;color:var(--text)!important;font-family:var(--ff)!important;font-size:13px!important;}
.stTextInput input:focus{border-color:var(--indigo)!important;box-shadow:0 0 0 3px var(--ind-dim)!important;}
.stTextInput input::placeholder{color:var(--text4)!important;}
.stRadio>div{flex-direction:row!important;gap:4px!important;background:var(--white)!important;border:1px solid var(--border)!important;border-radius:10px!important;padding:4px!important;display:inline-flex!important;box-shadow:var(--sh)!important;}
.stRadio label{font-family:var(--ff)!important;font-size:13px!important;font-weight:500!important;color:var(--text3)!important;padding:6px 14px!important;border-radius:7px!important;cursor:pointer!important;transition:all .15s!important;text-transform:none!important;letter-spacing:0!important;}
.stRadio label:has(input:checked){background:var(--indigo)!important;color:white!important;}

[data-testid="stChatMessage"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--r)!important;box-shadow:var(--sh)!important;}
[data-testid="stChatMessageContent"] *{font-family:var(--ff)!important;font-size:14px!important;color:var(--text)!important;line-height:1.7!important;}
[data-testid="stChatInput"] textarea{background:var(--white)!important;border:1px solid var(--border2)!important;border-radius:10px!important;color:var(--text)!important;font-family:var(--ff)!important;font-size:14px!important;}
[data-testid="stChatInput"] textarea:focus{border-color:var(--indigo)!important;box-shadow:0 0 0 3px var(--ind-dim)!important;}
[data-testid="stChatInput"] button{background:var(--indigo)!important;color:white!important;border-radius:8px!important;}
.stSpinner>div{border-top-color:var(--indigo)!important;}
hr{border-color:var(--border)!important;margin:16px 0!important;}
::-webkit-scrollbar{width:4px;height:4px;}::-webkit-scrollbar-track{background:transparent;}::-webkit-scrollbar-thumb{background:var(--border2);border-radius:4px;}

/* ── CUSTOM COMPONENTS ── */
.badge{font-family:var(--mono);font-size:11px;font-weight:500;padding:3px 10px;border-radius:20px;white-space:nowrap;display:inline-block;letter-spacing:.01em;}
.badge-red   {background:var(--red-dim); color:var(--red);    border:1px solid rgba(220,38,38,.15);}
.badge-orange{background:var(--org-dim); color:var(--orange); border:1px solid rgba(234,88,12,.15);}
.badge-green {background:var(--grn-dim); color:var(--green);  border:1px solid rgba(22,163,74,.15);}
.badge-indigo{background:var(--ind-dim); color:var(--indigo); border:1px solid var(--ind-mid);}
.badge-teal  {background:var(--teal-dim);color:var(--teal);   border:1px solid rgba(13,148,136,.15);}
.badge-gray  {background:var(--bg2);     color:var(--text3);  border:1px solid var(--border);}

.sec{font-size:11px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:14px;display:flex;align-items:center;gap:10px;}
.sec::after{content:'';flex:1;height:1px;background:var(--border);}

.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:20px 22px;box-shadow:var(--sh);margin-bottom:8px;}

.arow{display:flex;align-items:center;background:var(--card);border:1px solid var(--border);border-left:4px solid var(--border2);border-radius:0 var(--r) var(--r) 0;margin-bottom:8px;box-shadow:var(--sh);overflow:hidden;transition:all .15s;}
.arow:hover{box-shadow:var(--sh2);border-color:var(--border2);}
.arow-in{display:flex;align-items:center;gap:16px;padding:14px 18px;flex:1;min-width:0;}
.arow-n{font-family:var(--mono);font-size:11px;color:var(--text4);min-width:24px;flex-shrink:0;}
.arow-b{flex:1;min-width:0;}
.arow-name{font-size:14px;font-weight:600;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:4px;}
.arow-meta{font-family:var(--mono);font-size:11px;color:var(--text3);}
.arow-r{display:flex;align-items:center;gap:10px;flex-shrink:0;}

.srow{display:flex;align-items:center;gap:16px;background:var(--card);border:1px solid var(--border);border-left:4px solid var(--indigo);border-radius:0 var(--r2) var(--r2) 0;padding:12px 16px;margin-bottom:6px;box-shadow:var(--sh);transition:all .15s;}
.srow.submit{border-left-color:var(--red);}
.srow.review{border-left-color:var(--orange);}
.srow:hover{box-shadow:var(--sh2);}
.srow-t{font-family:var(--mono);font-size:13px;font-weight:500;color:var(--indigo);min-width:54px;flex-shrink:0;}
.srow.submit .srow-t{color:var(--red);}
.srow.review .srow-t{color:var(--orange);}
.srow-d{width:1px;height:28px;background:var(--border);flex-shrink:0;}
.srow-b{flex:1;min-width:0;}
.srow-task{font-size:13px;font-weight:600;color:var(--text);margin-bottom:3px;}
.srow-due{font-family:var(--mono);font-size:11px;color:var(--text3);}
.srow-r{display:flex;align-items:center;gap:8px;flex-shrink:0;}

.dhdr{font-size:12px;font-weight:700;color:var(--text2);padding:16px 0 8px;display:flex;align-items:center;gap:10px;}
.dhdr-today{padding:3px 10px;background:var(--ind-dim);color:var(--indigo);border-radius:20px;font-size:10px;font-weight:700;}
.dhdr-line{flex:1;height:1px;background:var(--border);}

.rrow{display:flex;align-items:center;background:var(--card);border:1px solid rgba(220,38,38,.15);border-left:4px solid var(--red);border-radius:0 var(--r) var(--r) 0;margin-bottom:10px;box-shadow:var(--sh);overflow:hidden;transition:all .15s;}
.rrow:hover{box-shadow:var(--sh2);}
.rrow-in{display:flex;align-items:center;gap:16px;padding:16px 18px;flex:1;}
.rrow-b{flex:1;min-width:0;}
.rrow-name{font-size:15px;font-weight:700;color:var(--text);margin-bottom:4px;}
.rrow-meta{font-family:var(--mono);font-size:11px;color:var(--text3);}
.rrow-r{display:flex;align-items:center;gap:12px;flex-shrink:0;}
.rrow-days{text-align:right;}
.rrow-num{font-size:28px;font-weight:800;color:var(--red);line-height:1;}
.rrow-lbl{font-size:10px;color:var(--text3);font-weight:500;}

.remrow{display:flex;align-items:center;gap:14px;background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:14px 18px;margin-bottom:8px;box-shadow:var(--sh);transition:all .15s;}
.remrow:hover{box-shadow:var(--sh2);}
.remrow.due-today{border-color:rgba(220,38,38,.2);background:rgba(220,38,38,.02);}
.remrow-icon{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;}
.remrow-b{flex:1;}
.remrow-title{font-size:13px;font-weight:600;color:var(--text);margin-bottom:3px;}
.remrow-meta{font-family:var(--mono);font-size:11px;color:var(--text3);}

.alert{display:flex;align-items:flex-start;gap:12px;padding:14px 18px;border-radius:var(--r);margin-bottom:10px;font-size:13px;font-weight:500;}
.alert-icon{font-size:18px;flex-shrink:0;margin-top:1px;}
.alert-bd{flex:1;}
.alert-title{font-weight:700;margin-bottom:2px;}
.alert-sub{font-size:12px;opacity:.75;}
.alert-red {background:var(--red-dim); border:1px solid rgba(220,38,38,.2);  color:var(--red);}
.alert-org {background:var(--org-dim); border:1px solid rgba(234,88,12,.2);  color:var(--orange);}
.alert-grn {background:var(--grn-dim); border:1px solid rgba(22,163,74,.2);  color:var(--green);}

.ovs{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:14px 18px;margin-bottom:6px;box-shadow:var(--sh);display:flex;align-items:center;justify-content:space-between;}
.ovs-l{font-size:12px;font-weight:600;color:var(--text3);}
.ovs-v{font-size:20px;font-weight:800;color:var(--text);}

.sync-card{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--border2);border-radius:0 var(--r) var(--r) 0;padding:16px 20px;box-shadow:var(--sh);margin-bottom:16px;}
.sync-ok {border-left-color:var(--teal);}
.sync-err{border-left-color:var(--red);}

.pbar-bg{background:var(--bg2);border-radius:4px;height:6px;overflow:hidden;margin-top:8px;}
.pbar-f{height:100%;border-radius:4px;transition:width .6s;}

.pghdr{margin-bottom:28px;padding-bottom:22px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;}
.pgtitle{font-size:26px;font-weight:800;color:var(--text);letter-spacing:-.03em;line-height:1;}
.pgtitle span{color:var(--indigo);}
.pgsub{font-size:13px;color:var(--text3);margin-top:5px;}
.pgts{font-family:var(--mono);font-size:12px;color:var(--text3);text-align:right;line-height:1.9;}

.hero{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:52vh;text-align:center;gap:18px;padding:48px 40px 32px;}
.hero-title{font-size:52px;font-weight:800;color:var(--text);letter-spacing:-.04em;line-height:1.05;}
.hero-title span{color:var(--indigo);}
.hero-sub{font-size:15px;color:var(--text3);max-width:440px;line-height:1.6;}
.hero-chips{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:4px 0;}
.hero-chip{font-size:12px;font-weight:600;color:var(--text2);background:var(--card);border:1px solid var(--border);padding:6px 14px;border-radius:20px;box-shadow:var(--sh);}

.sb-logo{padding:22px 20px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px;}
.sb-logo-icon{width:36px;height:36px;background:var(--indigo);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;}
.sb-logo-name{font-size:16px;font-weight:800;color:var(--text);letter-spacing:-.02em;}
.sb-logo-sub{font-size:11px;color:var(--text3);margin-top:1px;}
.sbrow{display:flex;align-items:center;justify-content:space-between;padding:10px 20px;border-bottom:1px solid var(--border);}
.sbrow-l{font-size:12px;font-weight:500;color:var(--text3);}
.sbrow-v{font-size:16px;font-weight:800;color:var(--text);}
.st-dot{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;padding:5px 12px;border-radius:20px;}
.pulse{animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.empty-s{text-align:center;padding:48px 20px;color:var(--text3);font-size:13px;}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ───────────────────────────────────────────────────────────────────
def urgency_badge(days):
    try: d = int(days)
    except: return "badge-gray", "—"
    if d <= 0:  return "badge-red",    "Overdue"
    if d == 1:  return "badge-red",    "Tomorrow"
    if d <= 3:  return "badge-orange", f"{d}d left"
    if d <= 7:  return "badge-green",  f"{d}d left"
    return "badge-gray", f"{d}d left"

def border_color(days):
    try: d = int(days)
    except: return "var(--border2)"
    if d <= 1: return "var(--red)"
    if d <= 3: return "var(--orange)"
    if d <= 7: return "var(--green)"
    return "var(--border2)"

def task_type(instr):
    s = str(instr)
    if "Submit"       in s: return "submit"
    if "Final review" in s: return "review"
    return "study"

def task_badge(instr):
    t = task_type(instr)
    if t == "submit": return "badge-red",    "Submit"
    if t == "review": return "badge-orange", "Review"
    return "badge-indigo", "Study"

def day_label(d):
    try:
        dt   = pd.to_datetime(d)
        diff = (dt.date() - _dt.date.today()).days
        if diff == 0: return "Today", True
        if diff == 1: return "Tomorrow", False
        return dt.strftime("%A, %d %b"), False
    except:
        return str(d), False

def add_single_event(row_data, event_type="session"):
    """Add one session or one deadline to Google Calendar."""
    try:
        service = st.session_state.get("_cal_service") or authenticate_google_calendar()
        if event_type == "session":
            task  = row_data.get("Task_Instruction", "Study Session")
            date  = row_data.get("Scheduled_Date",   str(_dt.date.today()))
            time  = row_data.get("Scheduled_Time",   "18:00")
            due   = row_data.get("due_date",         "—")
            color = "11" if "Submit" in str(task) else "5"
            parts = list(map(int, str(date).split("-")))
            hour  = int(str(time).split(":")[0])
            start = _dt.datetime(*parts, hour)
            end   = start + _dt.timedelta(hours=2)
            event = {
                "summary":     task,
                "description": f"AI_STUDY_PLANNER\nDue: {due}",
                "start": {"dateTime": start.isoformat(), "timeZone": "Asia/Kuala_Lumpur"},
                "end":   {"dateTime": end.isoformat(),   "timeZone": "Asia/Kuala_Lumpur"},
                "colorId": color,
                "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 30}]}
            }
        else:  # deadline
            name  = row_data.get("assignment_name", "Assignment Due")
            due   = str(row_data.get("due_date", str(_dt.date.today())))[:10]
            event = {
                "summary":     f"📌 DEADLINE: {name}",
                "description": f"AI_STUDY_PLANNER\nDeadline for {name}",
                "start": {"date": due},
                "end":   {"date": due},
                "colorId": "11",
                "reminders": {"useDefault": False, "overrides": [
                    {"method": "popup", "minutes": 1440},
                    {"method": "popup", "minutes": 60},
                ]}
            }
        service.events().insert(calendarId="primary", body=event).execute()
        return True, None
    except Exception as e:
        return False, str(e)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
      <div class="sb-logo-icon">🎓</div>
      <div>
        <div class="sb-logo-name">StudyPlanner</div>
        <div class="sb-logo-sub">AI-Powered Study Planner</div>
      </div>
    </div>""", unsafe_allow_html=True)

    loaded = st.session_state.get("df") is not None

    if loaded:
        df_s  = st.session_state["df"]
        sch_s = st.session_state["schedule"]
        rsk_s = st.session_state["risk_df"]
        rem_s = st.session_state["reminders"]
        st.markdown("""
        <div style="padding:12px 20px;border-bottom:1px solid var(--border)">
          <div class="st-dot" style="background:var(--grn-dim);color:var(--green)">
            <span class="pulse" style="width:7px;height:7px;border-radius:50%;background:var(--green);display:inline-block"></span>
            Canvas Connected
          </div>
        </div>""", unsafe_allow_html=True)
        for lbl, val, color in [
            ("Assignments",  len(df_s),  "var(--text)"),
            ("Scheduled",    len(sch_s), "var(--indigo)"),
            ("High Risk",    len(rsk_s), "var(--red)"    if len(rsk_s)>0 else "var(--text)"),
            ("Reminders",    len(rem_s), "var(--orange)" if len(rem_s)>0 else "var(--text)"),
        ]:
            st.markdown(f"""
            <div class="sbrow">
              <div class="sbrow-l">{lbl}</div>
              <div class="sbrow-v" style="color:{color}">{val}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding:12px 20px;border-bottom:1px solid var(--border)">
          <div class="st-dot" style="background:var(--bg2);color:var(--text3)">
            <span style="width:7px;height:7px;border-radius:50%;background:var(--text4);display:inline-block"></span>
            Not Connected
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="padding:14px 20px;border-bottom:1px solid var(--border)">
      <div style="font-size:11px;font-weight:600;color:var(--text3);margin-bottom:6px">System</div>
      <div style="font-family:var(--mono);font-size:13px;font-weight:500;color:var(--text)">{_dt.datetime.now().strftime("%H:%M")}</div>
      <div style="font-family:var(--mono);font-size:11px;color:var(--text3);margin-top:2px">{_dt.datetime.now().strftime("%A, %d %b %Y")}</div>
    </div>
    </div>""", unsafe_allow_html=True)


# ── PAGE HEADER ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="pghdr">
  <div>
    <div class="pgtitle">Agentic <span>AI</span> StudyPlanner</div>
    <div class="pgsub">Canvas LMS · Google Calendar ·  Chatbot</div>
  </div>
  <div class="pgts">{"● Live" if loaded else "○ Awaiting data"}<br>{_dt.datetime.now().strftime("%d %b %Y, %H:%M")}</div>
</div>""", unsafe_allow_html=True)


# ── LOAD BUTTON ───────────────────────────────────────────────────────────────
if not loaded:
    st.markdown("""
    <div class="hero">
      <div class="hero-title">Your AI<br><span>Study Planner</span></div>
      <div class="hero-sub">Connect to Canvas LMS to track deadlines, build your study schedule, and sync everything to Google Calendar automatically.</div>
      <div class="hero-chips">
        <span class="hero-chip">📋 Deadline Tracker</span>
        <span class="hero-chip">📅 Calendar Sync</span>
        <span class="hero-chip">🧠 Smart Scheduler</span>
        <span class="hero-chip">💬 AI Assistant</span>
        <span class="hero-chip">⚠️ Risk Alerts</span>
      </div>
    </div>""", unsafe_allow_html=True)

_, cc, _ = st.columns([2, 1, 2])
with cc:
    st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
    load_clicked = st.button("🚀  Load My Data from Canvas", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

if load_clicked:
    with st.spinner("Fetching from Canvas LMS and running AI pipeline..."):

        # ── BACKEND  ──────────────────────────────────
        courses = get_courses()
        all_assignments = []
        for course in courses:
            try:
                assignments = fetch_assignments(course["id"])
            except:
                continue
            for a in assignments:
                a["course_name"] = course["name"]
            all_assignments.extend(assignments)

        df = assignments_to_df(all_assignments)

        if df.empty:
            st.warning("No assignments found.")
        else:
            df = preprocess_new_assignments(df)
            df = predict_priorities(df)
            risk_df = detect_risk(df)

            service = authenticate_google_calendar()
            st.session_state["_cal_service"] = service   # cache — avoids re-auth
            events  = get_existing_events(service)

            schedule  = smart_schedule(df, events, risk_df)
            reminders = generate_reminders(schedule)

            # ADD URGENCY — identical to original
            df["due_date"] = pd.to_datetime(df["due_date"]).dt.tz_localize(None)
            today = pd.Timestamp.now().tz_localize(None)
            df["days_left"] = (df["due_date"] - today).dt.days

            def urgency(x):
                if x <= 1:   return "🔴 Urgent"
                elif x <= 3: return "🟡 Soon"
                else:        return "🟢 Safe"

            df["urgency"] = df["days_left"].apply(urgency)

            st.session_state["df"]        = df
            st.session_state["schedule"]  = schedule
            st.session_state["risk_df"]   = risk_df
            st.session_state["reminders"] = reminders
            st.rerun()


# ── MAIN UI ───────────────────────────────────────────────────────────────────
if st.session_state.get("df") is not None:

    df        = st.session_state["df"]
    schedule  = st.session_state["schedule"]
    risk_df   = st.session_state["risk_df"]
    reminders = st.session_state["reminders"]

    score  = max(0, 100 - (len(risk_df) * 10))
    urgent = df[df["days_left"] <= 1]

    # ── METRICS ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Assignments",  len(df))
    with c2: st.metric("Scheduled",    len(schedule))
    with c3: st.metric("High Risk",    len(risk_df))
    with c4: st.metric("Productivity", f"{score}%")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── ALERTS  ─────────────────────────────
    if len(risk_df) > 0:
        st.markdown(f"""
        <div class="alert alert-red">
          <div class="alert-icon">⚠️</div>
          <div class="alert-bd">
            <div class="alert-title">{len(risk_df)} High-Risk Task(s) Detected</div>
            <div class="alert-sub">Immediate attention required — check the Risk Alerts tab.</div>
          </div>
        </div>""", unsafe_allow_html=True)
    if not urgent.empty:
        st.markdown(f"""
        <div class="alert alert-org">
          <div class="alert-icon">⏰</div>
          <div class="alert-bd">
            <div class="alert-title">{len(urgent)} Assignment(s) Due Tomorrow</div>
            <div class="alert-sub">Review your schedule and prepare for submission.</div>
          </div>
        </div>""", unsafe_allow_html=True)
    if len(risk_df) == 0 and urgent.empty:
        st.markdown("""
        <div class="alert alert-grn">
          <div class="alert-icon">✅</div>
          <div class="alert-bd">
            <div class="alert-title">All Tasks Under Control</div>
            <div class="alert-sub">No urgent deadlines. Keep up the great work!</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── TODAY + OVERVIEW ──────────────────────────────────────────────────────
    left, right = st.columns([2.2, 1])

    with left:
        st.markdown('<div class="sec">Today\'s Focus Plan</div>', unsafe_allow_html=True)
        ts  = str(pd.Timestamp.now().date())
        tsc = schedule[schedule["Scheduled_Date"] == ts] if not schedule.empty else pd.DataFrame()
        top = tsc if not tsc.empty else schedule.head(5)
        if top.empty:
            st.markdown('<div class="empty-s">No sessions scheduled for today</div>', unsafe_allow_html=True)
        else:
            for _, row in top.iterrows():
                instr = row.get("Task_Instruction","—")
                ts_   = row.get("Scheduled_Time","—")
                due   = row.get("due_date","—")
                tt    = task_type(instr)
                bc,bl = task_badge(instr)
                st.markdown(f"""
                <div class="srow {tt}">
                  <div class="srow-t">{ts_}</div><div class="srow-d"></div>
                  <div class="srow-b"><div class="srow-task">{instr}</div><div class="srow-due">Due: {due}</div></div>
                  <span class="badge {bc}">{bl}</span>
                </div>""", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="sec">Overview</div>', unsafe_allow_html=True)
        for lbl, val, color in [
            ("Total Assignments", len(df),        "var(--text)"),
            ("Scheduled Tasks",   len(schedule),  "var(--indigo)"),
            ("High Risk",         len(risk_df),   "var(--red)"    if len(risk_df)>0 else "var(--green)"),
            ("Active Reminders",  len(reminders), "var(--orange)" if len(reminders)>0 else "var(--text)"),
        ]:
            st.markdown(f'<div class="ovs"><div class="ovs-l">{lbl}</div><div class="ovs-v" style="color:{color}">{val}</div></div>', unsafe_allow_html=True)
        sc = "var(--green)" if score>=70 else "var(--orange)" if score>=40 else "var(--red)"
        st.markdown(f"""
        <div class="card" style="margin-top:6px;padding:16px 18px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span style="font-size:12px;font-weight:600;color:var(--text3)">Productivity Score</span>
            <span style="font-size:20px;font-weight:800;color:{sc}">{score}%</span>
          </div>
          <div class="pbar-bg"><div class="pbar-f" style="width:{score}%;background:{sc}"></div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄  Assignments",
        "📅  Schedule & Calendar",
        "⚠️  Risk Alerts",
        "🤖  AI Assistant",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — ASSIGNMENTS
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="sec">All Assignments from Canvas</div>', unsafe_allow_html=True)
        if df.empty:
            st.markdown('<div class="empty-s">No assignments found. Check your Canvas connection.</div>', unsafe_allow_html=True)
        else:
            fc1, fc2 = st.columns([1.6, 3])
            with fc1:
                uf = st.selectbox("", ["All", "🔴 Urgent", "🟡 Soon", "🟢 Safe"],
                                  label_visibility="collapsed", key="uf")
            with fc2:
                sq = st.text_input("", placeholder="🔍  Search by name or course...",
                                   label_visibility="collapsed", key="sq")
            disp = df.copy()
            if uf != "All": disp = disp[disp["urgency"] == uf]
            if sq:
                disp = disp[
                    disp["assignment_name"].str.contains(sq, case=False, na=False) |
                    disp["course_name"].str.contains(sq, case=False, na=False)
                ]
            disp = disp.sort_values("days_left", ascending=True)

            st.markdown(f'<div class="sec" style="margin-top:16px">{len(disp)} assignment(s)</div>', unsafe_allow_html=True)

            for i, (_, row) in enumerate(disp.iterrows()):
                days  = int(row.get("days_left", 99))
                ub,ul = urgency_badge(days)
                bc    = border_color(days)
                name  = row.get("assignment_name","—")
                course= row.get("course_name","—")
                pts   = row.get("points","—")
                hrs   = row.get("estimated_hours","—")

                main_c, btn_c = st.columns([5, 1])
                with main_c:
                    st.markdown(f"""
                    <div class="arow" style="border-left-color:{bc}">
                      <div class="arow-in">
                        <div class="arow-n">{str(i+1).zfill(2)}</div>
                        <div class="arow-b">
                          <div class="arow-name">{name}</div>
                          <div class="arow-meta">{course} · {hrs}h estimated · {pts} pts</div>
                        </div>
                        <div class="arow-r"><span class="badge {ub}">{ul}</span></div>
                      </div>
                    </div>""", unsafe_allow_html=True)
                with btn_c:
                    st.markdown('<div class="btn-cal" style="margin-top:8px">', unsafe_allow_html=True)
                    if st.button("📅 Add Deadline", key=f"dl_{i}_{name[:8]}"):
                        ok, err = add_single_event(dict(row), event_type="deadline")
                        if ok: st.success("Deadline added to Google Calendar! ✅")
                        else:  st.error(f"Failed: {err}")
                    st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — SCHEDULE & GOOGLE CALENDAR
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        if schedule.empty:
            st.markdown('<div class="empty-s">No sessions scheduled yet.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="sec">Google Calendar Sync</div>', unsafe_allow_html=True)

            sub_c = len(schedule[schedule["Task_Instruction"].str.contains("Submit",       na=False)])
            rev_c = len(schedule[schedule["Task_Instruction"].str.contains("Final review", na=False)])
            stu_c = len(schedule) - sub_c - rev_c

            sc1,sc2,sc3,sc4 = st.columns(4)
            for col,lbl,val,color in [
                (sc1,"Total Events",   len(schedule),"var(--text)"),
                (sc2,"Study Sessions", stu_c,         "var(--indigo)"),
                (sc3,"Reviews",        rev_c,         "var(--orange)"),
                (sc4,"Submissions",    sub_c,         "var(--red)"),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="card" style="text-align:center;padding:16px 12px">
                      <div style="font-size:11px;font-weight:600;color:var(--text3);margin-bottom:6px">{lbl}</div>
                      <div style="font-size:28px;font-weight:800;color:{color}">{val}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

            cal_synced    = st.session_state.get("cal_synced",    False)
            cal_sync_time = st.session_state.get("cal_sync_time", None)
            cal_sync_err  = st.session_state.get("cal_sync_err",  None)

            info_c, btn_c = st.columns([3, 1])
            with info_c:
                if cal_sync_err:
                    st.markdown(f'<div class="sync-card sync-err"><div style="font-weight:700;color:var(--red);margin-bottom:4px">⚠️ Sync Failed</div><div style="font-size:12px;color:var(--text3)">{cal_sync_err}</div></div>', unsafe_allow_html=True)
                elif cal_synced and cal_sync_time:
                    st.markdown(f'<div class="sync-card sync-ok"><div style="font-weight:700;color:var(--teal);margin-bottom:4px">✅ {len(schedule)} events synced to Google Calendar</div><div style="font-size:12px;color:var(--text3)">Last synced: {cal_sync_time} · Asia/Kuala_Lumpur · 30 min popup reminders · 🟢 Study/Review · 🔴 Submit</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="sync-card"><div style="font-weight:700;color:var(--text);margin-bottom:4px">📅 Sync All {len(schedule)} Sessions to Google Calendar</div><div style="font-size:12px;color:var(--text3)">Pushes all study sessions, reviews, and submissions. Old AI events are cleared first. Color-coded and reminders attached.</div></div>', unsafe_allow_html=True)

            with btn_c:
                st.markdown('<div class="btn-teal" style="margin-top:4px">', unsafe_allow_html=True)
                if st.button("📅  Sync All", use_container_width=True, key="sync_all"):
                    with st.spinner("Syncing..."):
                        try:
                            svc = st.session_state.get("_cal_service") or authenticate_google_calendar()
                            delete_old_events(svc)
                            add_events_to_calendar(svc, schedule)
                            st.session_state["cal_synced"]    = True
                            st.session_state["cal_sync_time"] = _dt.datetime.now().strftime("%H:%M:%S, %d %b %Y")
                            st.session_state["cal_sync_err"]  = None
                            st.rerun()
                        except Exception as e:
                            st.session_state["cal_synced"]   = False
                            st.session_state["cal_sync_err"] = str(e)
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

            view = st.radio("", ["All","Today","This Week"],
                            horizontal=True, label_visibility="collapsed", key="sv")
            ts2 = str(pd.Timestamp.now().date())
            wk  = [str((pd.Timestamp.now()+pd.Timedelta(days=i)).date()) for i in range(7)]
            sf  = schedule.copy()
            if view=="Today":     sf = sf[sf["Scheduled_Date"]==ts2]
            elif view=="This Week":sf = sf[sf["Scheduled_Date"].isin(wk)]

            st.markdown('<div class="sec" style="margin-top:16px">Study Sessions</div>', unsafe_allow_html=True)

            if sf.empty:
                st.markdown('<div class="empty-s">No sessions for this period</div>', unsafe_allow_html=True)
            else:
                for d, grp in sf.groupby("Scheduled_Date", sort=True):
                    lbl, is_t = day_label(d)
                    tb = f'<span class="dhdr-today">Today</span>' if is_t else ''
                    st.markdown(f'<div class="dhdr">{lbl} {tb}<div class="dhdr-line"></div><span style="font-size:11px;color:var(--text3);font-weight:500">{len(grp)} session(s)</span></div>', unsafe_allow_html=True)
                    for ri, (_, row) in enumerate(grp.iterrows()):
                        instr = row.get("Task_Instruction","—")
                        ts_   = row.get("Scheduled_Time","—")
                        due   = row.get("due_date","—")
                        tt    = task_type(instr)
                        bc,bl = task_badge(instr)
                        try: es = f"{int(ts_.split(':')[0])+2:02d}:00"
                        except: es = "—"

                        rc, ac = st.columns([5, 1])
                        with rc:
                            st.markdown(f"""
                            <div class="srow {tt}">
                              <div style="display:flex;flex-direction:column;min-width:58px;flex-shrink:0">
                                <div class="srow-t">{ts_}</div>
                                <div style="font-family:var(--mono);font-size:10px;color:var(--text3)">→ {es}</div>
                              </div>
                              <div class="srow-d"></div>
                              <div class="srow-b"><div class="srow-task">{instr}</div><div class="srow-due">Due: {due}</div></div>
                              <span class="badge {bc}">{bl}</span>
                            </div>""", unsafe_allow_html=True)
                        with ac:
                            st.markdown('<div class="btn-cal" style="margin-top:8px">', unsafe_allow_html=True)
                            if st.button("📅 Add", key=f"s_{d}_{ri}_{ts_}"):
                                ok, err = add_single_event(dict(row), event_type="session")
                                if ok: st.success("Added! ✅")
                                else:  st.error(f"Failed: {err}")
                            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec">Deadline Reminders</div>', unsafe_allow_html=True)
        if reminders.empty:
            st.markdown('<div class="empty-s">No active reminders<br><span style="font-size:12px">Fires for submission tasks due today or in 4 days</span></div>', unsafe_allow_html=True)
        else:
            td = _dt.date.today()
            for _, row in reminders.iterrows():
                rt  = row.get("Reminder","—")
                due = row.get("Due_Date","—")
                ito = str(due)==str(td)
                icon= "🔴" if ito else "🔔"
                bg  = "rgba(220,38,38,0.08)" if ito else "rgba(234,88,12,0.08)"
                rc,rl=("badge-red","Due Today") if ito else ("badge-orange","Upcoming")
                st.markdown(f"""
                <div class="remrow {'due-today' if ito else ''}">
                  <div class="remrow-icon" style="background:{bg}">{icon}</div>
                  <div class="remrow-b"><div class="remrow-title">{rt}</div><div class="remrow-meta">Due: {due}</div></div>
                  <span class="badge {rc}">{rl}</span>
                </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — RISK ALERTS
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        if risk_df.empty:
            st.markdown("""
            <div class="alert alert-grn">
              <div class="alert-icon">✅</div>
              <div class="alert-bd"><div class="alert-title">No High-Risk Tasks</div>
              <div class="alert-sub">All assignments are on track. Keep it up!</div></div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert alert-red">
              <div class="alert-icon">⚠️</div>
              <div class="alert-bd"><div class="alert-title">{len(risk_df)} High-Risk Task(s) — Immediate Action Required</div>
              <div class="alert-sub">XGBoost priority = 2 AND days_until_due ≤ 7. These deadlines need attention now.</div></div>
            </div>""", unsafe_allow_html=True)

            st.markdown('<div class="sec" style="margin-top:16px">Risk Assessment</div>', unsafe_allow_html=True)

            dr = risk_df.sort_values("risk_score", ascending=False) if "risk_score" in risk_df.columns else risk_df
            for ri, (_, row) in enumerate(dr.iterrows()):
                aname  = row.get("assignment_name","—")
                due    = row.get("due_date","—")
                days   = int(row.get("days_until_due", 0))
                course = row.get("course_name","")
                rs     = f"{float(row.get('risk_score',0)):.3f}" if "risk_score" in row.index else "—"

                rc, ac = st.columns([5, 1])
                with rc:
                    st.markdown(f"""
                    <div class="rrow">
                      <div class="rrow-in">
                        <div style="font-size:22px;flex-shrink:0">⚠️</div>
                        <div class="rrow-b"><div class="rrow-name">{aname}</div>
                        <div class="rrow-meta">{course} · Due: {due} · Risk Score: {rs}</div></div>
                        <div class="rrow-r"><div class="rrow-days">
                          <div class="rrow-num">{days}</div>
                          <div class="rrow-lbl">days left</div>
                        </div></div>
                      </div>
                    </div>""", unsafe_allow_html=True)
                with ac:
                    st.markdown('<div class="btn-cal" style="margin-top:12px">', unsafe_allow_html=True)
                    if st.button("📅 Add Deadline", key=f"r_{ri}_{aname[:8]}"):
                        ok, err = add_single_event(dict(row), event_type="deadline")
                        if ok: st.success("Added! ✅")
                        else:  st.error(f"Failed: {err}")
                    st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — AI CHAT ASSISTANT 
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="sec">AI Study Assistant</div>', unsafe_allow_html=True)

        qc1, qc2, qc3 = st.columns(3)
        for col, prompt in {
            qc1: "What assignments are due this week?",
            qc2: "Plan my study schedule",
            qc3: "What should I study today?",
        }.items():
            with col:
                st.markdown('<div class="qbtn">', unsafe_allow_html=True)
                if st.button(prompt, use_container_width=True, key=f"qp_{prompt}"):
                    if "chat_history" not in st.session_state:
                        st.session_state.chat_history = []
                    response = smart_assistant(prompt, safe_df_for_assistant(df), schedule)
                    st.session_state.chat_history.append(("You", prompt))
                    st.session_state.chat_history.append(("Bot", response))
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for role, msg in st.session_state.chat_history:
            if role == "You":
                st.chat_message("user",      avatar="🎓").write(msg)
            else:
                st.chat_message("assistant", avatar="🤖").write(msg)

        user_input = st.chat_input("Ask your AI study assistant...")
        if user_input:
            response = smart_assistant(user_input, safe_df_for_assistant(df), schedule)
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("Bot", response))
            st.rerun()

else:
    if not st.session_state.get("df"):
        st.markdown('<div style="text-align:center;color:var(--text3);font-size:13px;margin-top:8px">Click the button above to connect to Canvas LMS</div>', unsafe_allow_html=True)