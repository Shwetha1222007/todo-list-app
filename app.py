import streamlit as st
from datetime import datetime, timedelta
import time
import pytz
import json
import os

# 1. Page Configuration
st.set_page_config(page_title="TaskMaster Pro - Autonomous Alarm", page_icon="⏰", layout="wide")

# 2. IST Timezone Setup
IST = pytz.timezone('Asia/Kolkata')
TASKS_FILE = "tasks.json"

# 3. Premium High-Gloss Design (CSS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #050505;
        color: #f8fafc;
    }
    
    .stApp { background: #050505; }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        margin-bottom: 24px;
    }
    
    .ringing-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 60px;
        background: #ef4444; color: white; display: flex; align-items: center;
        justify-content: center; z-index: 9999; font-weight: 800; font-size: 1.2rem;
        animation: slide-down 0.5s ease-out;
    }
    
    @keyframes slide-down { from { transform: translateY(-100%); } to { transform: translateY(0); } }
    
    .clock-hero {
        text-align: center;
        padding: 40px 0;
        background: radial-gradient(circle at center, rgba(99, 102, 241, 0.1) 0%, transparent 80%);
    }
    
    .clock-digit {
        font-size: 6rem;
        font-weight: 800;
        letter-spacing: -2px;
        background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .status-active { border: 2px solid #ef4444 !important; background: rgba(239, 68, 68, 0.1) !important; animation: glow-red 1.5s infinite; }
    @keyframes glow-red { 0% { box-shadow: 0 0 5px rgba(239, 68, 68, 0.2); } 50% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.5); } 100% { box-shadow: 0 0 5px rgba(239, 68, 68, 0.2); } }
    
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.2s;
    }
</style>
""", unsafe_allow_html=True)

# 4. Persistence Functions
def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f)

# Initialize Session State
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

if "audio_ready" not in st.session_state:
    st.session_state.audio_ready = False

# 5. Background Alarm Engine (Autonomous Check)
now_ist = datetime.now(IST)
current_ts_ms = int(now_ist.timestamp() * 1000)
active_alarms = []
state_changed = False

# Check Alarms
for t in st.session_state.tasks:
    if t['status'] == 'pending' and current_ts_ms >= t['ts']:
        t['status'] = 'ringing'
        state_changed = True
        st.toast(f"🔔 ALERT: {t['name']}", icon="⏰")
    
    if t['status'] == 'ringing':
        active_alarms.append(t['name'])

if state_changed:
    save_tasks(st.session_state.tasks)

# Global Trigger UI
if active_alarms:
    st.markdown(f'<div class="ringing-overlay">🚨 TIME\'S UP: {", ".join(active_alarms)}</div>', unsafe_allow_html=True)
    if st.session_state.audio_ready:
        st.markdown('<audio autoplay loop><source src="https://www.soundjay.com/buttons/beep-07a.mp3"></audio>', unsafe_allow_html=True)

# 6. Sidebar: Mandatory System Warm-up
with st.sidebar:
    st.title("🛡️ Core Settings")
    
    # Audio Activation Status
    if not st.session_state.audio_ready:
        st.warning("⚠️ Audio System Inactive")
        if st.button("🔌 ACTIVATE ALARM SYSTEM", use_container_width=True, type="primary"):
            st.session_state.audio_ready = True
            st.markdown('<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3"></audio>', unsafe_allow_html=True)
            st.rerun()
    else:
        st.success("✅ AUDIO ENGINE STANDBY")
        if active_alarms:
            if st.button("🔇 SILENCE ALL", use_container_width=True):
                for t in st.session_state.tasks:
                    if t['status'] == 'ringing': t['status'] = 'completed'
                save_tasks(st.session_state.tasks)
                st.rerun()

    st.divider()
    pending_count = len([t for t in st.session_state.tasks if t['status'] == 'pending'])
    st.metric("Future Reminders", pending_count)
    
    if st.button("🗑️ Reset Everything"):
        st.session_state.tasks = []
        st.session_state.audio_ready = False
        save_tasks([])
        st.rerun()

# 7. Hero: Live IST Sync Clock
st.markdown(f"""
    <div class="clock-hero">
        <h1 id="ist-clock" class="clock-digit">--:--:--</h1>
        <p style="color: #6366f1; letter-spacing: 5px; font-weight: 700; font-size: 0.9rem;">IST AUTONOMOUS SYNC</p>
    </div>
    <script>
        function updateIST() {{
            const options = {{ timeZone: 'Asia/Kolkata', hour12: true, hour: '2-digit', minute: '2-digit', second: '2-digit' }};
            document.getElementById('ist-clock').innerText = new Date().toLocaleTimeString('en-IN', options);
        }}
        setInterval(updateIST, 1000);
        updateIST();
    </script>
""", unsafe_allow_html=True)

# 8. Main Dashboard
col_left, col_right = st.columns([1, 1.5])

with col_left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("➕ Create Schedule")
    with st.form("task_creation", clear_on_submit=True):
        t_label = st.text_input("What is the task?", placeholder="e.g. Call Client")
        t_date = st.date_input("Select Date", now_ist.date())
        
        st.write("Set Time (12-Hour):")
        c1, c2, c3 = st.columns(3)
        h = c1.selectbox("Hr", list(range(1, 13)), index=now_ist.hour % 12 - 1 if now_ist.hour % 12 != 0 else 11)
        m = c2.selectbox("Min", [f"{i:02d}" for i in range(60)], index=now_ist.minute)
        ap = c3.selectbox("Format", ["AM", "PM"], index=0 if now_ist.hour < 12 else 1)
        
        # Submitting the form REGISTER the task into the background scheduler
        if st.form_submit_button("ADD SCHEDULE", use_container_width=True):
            h24 = h
            if ap == "PM" and h != 12: h24 += 12
            elif ap == "AM" and h == 12: h24 = 0
            
            target_dt = IST.localize(datetime.combine(t_date, datetime.min.time().replace(hour=h24, minute=int(m))))
            target_ts = int(target_dt.timestamp() * 1000)
            
            if target_ts <= current_ts_ms:
                st.error("❌ Time has already passed in IST!")
            elif not t_label:
                st.error("❌ Task description is required")
            else:
                new_task = {
                    "id": time.time(),
                    "name": t_label,
                    "ts": target_ts,
                    "time_str": target_dt.strftime("%I:%M %p"),
                    "status": "pending"
                }
                st.session_state.tasks.append(new_task)
                save_tasks(st.session_state.tasks)
                
                # Auto-activate audio on interaction
                st.session_state.audio_ready = True
                
                st.success(f"Registered for {target_dt.strftime('%I:%M %p')}")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📋 Autonomous Feed")
    
    # Priority: Ringing first, then Pending, then Done
    prio = {"ringing": 0, "pending": 1, "completed": 2}
    sorted_tasks = sorted(st.session_state.tasks, key=lambda x: (prio[x['status']], x['ts']))

    if not sorted_tasks:
        st.info("The scheduler is currently idle. Add a task to begin monitoring.")

    for t in sorted_tasks:
        is_ringing = t['status'] == 'ringing'
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.02); padding: 16px; border-radius: 16px; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.05);" class="{'status-active' if is_ringing else ''}">
                <div style="display:flex; justify-content: space-between; align-items:center;">
                    <div>
                        <div style="font-size: 0.7rem; font-weight: 800; color: #6366f1; text-transform: uppercase; letter-spacing: 1px;">{t['status']}</div>
                        <b style="font-size: 1.1rem; color: #f1f5f9;">{t['name']}</b><br>
                        <span style="color: #94a3b8; font-size: 0.85rem;">⏰ IST Target: {t['time_str']}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if is_ringing:
            st.error(f"🚨 ALERT: {t['name']}!")
            st.balloons()
            if st.button(f"STOP & COMPLETE: {t['name']}", key=f"stop_{t['id']}", use_container_width=True):
                t['status'] = 'completed'
                save_tasks(st.session_state.tasks)
                st.rerun()
        
        elif t['status'] == 'pending':
            if st.button("Cancel Task", key=f"del_{t['id']}"):
                st.session_state.tasks = [tk for tk in st.session_state.tasks if tk['id'] != t['id']]
                save_tasks(st.session_state.tasks)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# 9. INTELLIGENT AUTONOMOUS LOOP
# Instead of blindly reloading the page (which kills session & audio state),
# we calculate exactly when the next alarm is due and wait for it server-side.
# This prevents disruption while ensuring the alarm triggering is AUTOMATIC.

pending_times = [t['ts'] for t in st.session_state.tasks if t['status'] == 'pending']

if pending_times:
    next_alarm_ts = min(pending_times)
    now_ts = int(time.time() * 1000)
    wait_ms = next_alarm_ts - now_ts
    
    # If alarm is within 1 hour, we enter a smart wait loop
    if wait_ms > 0 and wait_ms < 3600000:
        # We cap the wait to 5 seconds to stay responsive to potential drift 
        # or just to keep the app "alive" without freezing for too long.
        # 5 seconds is a good balance.
        sleep_sec = min(wait_ms / 1000, 5)
        if sleep_sec > 0.1:
            time.sleep(sleep_sec)
            st.rerun()
    elif wait_ms <= 0:
        # If we missed it or it's time, rerun immediately to trigger alarm logic
        st.rerun()
