import streamlit as st
from datetime import datetime, date
import time

# 1. Page Config
st.set_page_config(page_title="TaskMaster Pro - ALARM FIXED", page_icon="🚨", layout="wide")

# 2. Premium Styling (CSS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #f1f5f9; }
    
    .stApp { background: #f8fafc; }
    
    /* Global Alarm Overlay */
    .alarm-screen {
        position: fixed; top: 0; left: 0; width: 100%; padding: 20px;
        background: #ef4444; color: white; text-align: center;
        z-index: 1000; font-weight: bold; font-size: 1.5rem;
        animation: blink-bg 0.5s infinite alternate;
    }
    @keyframes blink-bg { from { background: #ef4444; } to { background: #b91c1c; } }
    
    .main-card {
        background: white; border-radius: 15px; padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 20px;
    }
    
    .task-pending { border-left: 5px solid #6366f1; background: #ffffff; }
    .task-ringing { border: 3px solid #ef4444 !important; background: #fee2e2 !important; animation: shake 0.5s infinite; }
    .task-done { border-left: 5px solid #10b981; background: #f0fdf4 !important; opacity: 0.6; }
    
    @keyframes shake {
        0% { transform: translateX(0); }
        25% { transform: translateX(5px); }
        50% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
        100% { transform: translateX(0); }
    }
</style>
""", unsafe_allow_html=True)

# 3. State Management
if "tasks" not in st.session_state: st.session_state.tasks = []
if "audio_on" not in st.session_state: st.session_state.audio_on = False

# 4. Sidebar: Must Click to Start
with st.sidebar:
    st.header("⚙️ Controller")
    if st.button("� ACTIVATE ALARM SYSTEM (Required)", use_container_width=True):
        st.session_state.audio_on = True
        st.success("System Active!")
        # Test sound
        st.markdown('<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3"></audio>', unsafe_allow_html=True)
    
    st.divider()
    st.title("📊 Statistics")
    total = len(st.session_state.tasks)
    ringing = len([t for t in st.session_state.tasks if t['status'] == 'ringing'])
    completed = len([t for t in st.session_state.tasks if t['status'] == 'completed'])
    
    st.metric("Tasks Alarming Now", ringing)
    st.metric("Tasks Finished", completed)
    
    if st.button("🗑️ Clear All Tasks"):
        st.session_state.tasks = []
        st.rerun()

# 5. Clock & Logic Sync
now_dt = datetime.now()
curr_ts = now_dt.timestamp()

# 6. Global Alarm Check (Before UI renders)
for t in st.session_state.tasks:
    if t['status'] == 'pending' and curr_ts >= t['target_ts']:
        t['status'] = 'ringing'
        # Force immediate update
        st.toast(f"🚨 ALARM: {t['name']}")

# 7. UI Dashboard
st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="margin: 0; color: #1e293b; font-size: 3.5rem;">{now_dt.strftime('%I:%M:%S %p')}</h1>
        <p style="color: #64748b; font-size: 1.2rem;">{now_dt.strftime('%A, %B %d, %Y')}</p>
    </div>
""", unsafe_allow_html=True)

# 8. Main Body
col_in, col_list = st.columns([1, 2])

with col_in:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("➕ Create Reminder")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("Task Title", placeholder="Enter task name...")
        d = st.date_input("Date", date.today())
        
        st.write("Clock Time:")
        c1, c2, c3 = st.columns(3)
        h = c1.selectbox("Hr", [i for i in range(1, 13)], index=now_dt.hour % 12 - 1 if now_dt.hour % 12 != 0 else 11)
        m = c2.selectbox("Min", [f"{i:02d}" for i in range(60)], index=now_dt.minute)
        ap = c3.selectbox("AM/PM", ["AM", "PM"], index=0 if now_dt.hour < 12 else 1)
        
        if st.form_submit_button("Start Alarm Countdown", use_container_width=True):
            # 12h to 24h conversion
            h24 = h
            if ap == "PM" and h != 12: h24 += 12
            elif ap == "AM" and h == 12: h24 = 0
            
            target_dt = datetime.combine(d, datetime.min.time().replace(hour=h24, minute=int(m)))
            
            if target_dt.timestamp() <= curr_ts:
                st.error("❌ Past time! Choose a future time.")
            elif not name:
                st.error("❌ Title required!")
            else:
                st.session_state.tasks.append({
                    "id": time.time(),
                    "name": name,
                    "target_ts": target_dt.timestamp(),
                    "time_str": target_dt.strftime("%I:%M %p"),
                    "status": "pending"
                })
                st.success("✅ Task Scheduled!")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_list:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📋 My Reminders")
    
    # Sort: Alarming first, then Pending, then Finished
    rank = {"ringing": 0, "pending": 1, "completed": 2}
    sorted_tasks = sorted(st.session_state.tasks, key=lambda x: (rank[x['status']], x['target_ts']))

    if not sorted_tasks:
        st.info("No reminders yet.")

    for t in sorted_tasks:
        card_class = f"task-{t['status']}"
        
        # Display Box
        st.markdown(f"""
            <div style="padding: 15px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #e2e8f0;" class="{card_class}">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="margin: 0; color: #1e293b;">{t['name']}</h3>
                        <span style="color: #64748b; font-size: 0.9rem;">⏰ {t['time_str']}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # BUTTON LOGIC
        if t['status'] == 'ringing':
            st.error(f"🚨 ALERT: {t['name']} is STARTING NOW!")
            # Trigger Balloons only on first switch
            st.balloons()
            
            # Sound Loop
            if st.session_state.audio_on:
                st.markdown('<audio autoplay loop><source src="https://www.soundjay.com/buttons/beep-07a.mp3"></audio>', unsafe_allow_html=True)
            
            if st.button(f"STOP ALARM & FINISH: {t['name']}", key=f"ring_{t['id']}", use_container_width=True):
                t['status'] = 'completed'
                st.rerun()
        
        elif t['status'] == 'pending':
            if st.button(f"🗑️ Cancel Reminder", key=f"del_{t['id']}"):
                st.session_state.tasks = [tk for tk in st.session_state.tasks if tk['id'] != t['id']]
                st.rerun()
        
        elif t['status'] == 'completed':
            st.success("Task Completed ✅")
            if st.button(f"🗑️ Remove from list", key=f"done_{t['id']}"):
                st.session_state.tasks = [tk for tk in st.session_state.tasks if tk['id'] != t['id']]
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# 9. Heartbeat Script (Updated for stability)
st.markdown("""
<script>
    setTimeout(function() {
        // Don't reload if user is typing
        if (!document.activeElement || document.activeElement.tagName !== 'INPUT') {
            window.location.reload();
        }
    }, 5000);
</script>
""", unsafe_allow_html=True)
