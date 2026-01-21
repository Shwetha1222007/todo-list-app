import streamlit as st
from datetime import datetime, date
import time
import base64

# Set page config
st.set_page_config(page_title="TaskMaster Pro", page_icon="⏰", layout="wide")

# Custom CSS for Premium Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        margin-bottom: 20px;
    }
    
    .task-item {
        background: white;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    
    .task-item:hover {
        transform: translateY(-2px);
    }
    
    .clock-container {
        text-align: center;
        padding: 20px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 30px;
    }
    
    .clock-time {
        font-size: 3rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    
    .clock-date {
        font-size: 1rem;
        color: #6b7280;
        margin-top: 5px;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 10px 25px;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# ---------- Live Clock UI ----------
# Pre-calculate initial time to avoid "Loading..." flash
initial_time = datetime.now().strftime("%I:%M:%S %p")
initial_date = datetime.now().strftime("%A, %B %d, %Y")

st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <span style="font-size: 0.8rem; font-weight: 600; color: #6366f1; text-transform: uppercase; letter-spacing: 1px;">Live System Clock</span>
        <div class="clock-container" style="margin-top: 5px; padding: 15px;">
            <p id="js-clock" class="clock-time" style="margin: 0;">{initial_time}</p>
            <p id="js-date" class="clock-date" style="margin: 0;">{initial_date}</p>
        </div>
    </div>
    <script>
        function updateClock() {{
            const now = new Date();
            const timeStr = now.toLocaleTimeString('en-US', {{ hour12: true, hour: '2-digit', minute: '2-digit', second: '2-digit' }});
            const dateStr = now.toLocaleDateString('en-US', {{ weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }});
            document.getElementById('js-clock').innerText = timeStr;
            document.getElementById('js-date').innerText = dateStr;
        }}
        setInterval(updateClock, 1000);
    </script>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ---------- Sidebar Stats ----------
with st.sidebar:
    st.title("📊 Statistics")
    total_tasks = len(st.session_state.tasks)
    active_tasks = len([t for t in st.session_state.tasks if not t['alerted']])
    completed_tasks = total_tasks - active_tasks
    
    st.metric("Total Tasks", total_tasks)
    st.metric("Active Reminders", active_tasks)
    
    if total_tasks > 0:
        st.write(f"Completion Rate: {int((completed_tasks/total_tasks)*100)}%")
        st.progress(completed_tasks/total_tasks)

# ---------- Main UI ----------
col1, col2 = st.columns([2, 1])

with col2:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("➕ New Task")
    
    # Use a form to prevent clearing inputs during auto-refresh
    with st.form("task_from", clear_on_submit=True):
        task_desc = st.text_input("What needs to be done?", placeholder="Enter task...")
        rem_date = st.date_input("Select Date", date.today())
        
        # FIX 1: Set step=60 to allow exact minute selection (e.g., 7:12, 7:18)
        # FIX 2: Default time is rounded to the current minute
        default_time = datetime.now().replace(second=0, microsecond=0).time()
        rem_time = st.time_input("Select Time (AM/PM supported by browser)", default_time, step=60)
        
        submitted = st.form_submit_button("Set Professional Alarm", use_container_width=True)
        
        if submitted:
            if task_desc:
                # FIX 3: Combine date and time into a single naive datetime for strict comparison
                scheduled_dt = datetime.combine(rem_date, rem_time)
                
                # Check if the user is trying to set a time that has already passed
                if scheduled_dt <= datetime.now():
                    st.error("Cannot set a reminder for a past time!")
                else:
                    st.session_state.tasks.append({
                        "task": task_desc,
                        "datetime": scheduled_dt,
                        "alerted": False
                    })
                    st.success(f"Alarm set for {scheduled_dt.strftime('%I:%M %p')}! 🎯")
                    st.rerun()
            else:
                st.error("Task description required")
    st.markdown('</div>', unsafe_allow_html=True)

with col1:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📋 Your Timeline")
    
    now = datetime.now()
    
    # Sort tasks by datetime
    sorted_tasks = sorted(st.session_state.tasks, key=lambda x: x['datetime'])
    
    if not sorted_tasks:
        st.info("No tasks yet. Add one to get started!")
    
    for i, t in enumerate(sorted_tasks):
        with st.container():
            is_due = now >= t["datetime"] and not t["alerted"]
            bg_color = "#fffbeb" if is_due else "white"
            border_color = "#fbbf24" if is_due else "#e5e7eb"
            
            due_str = t["datetime"].strftime("%d %b, %I:%M %p")
            
            st.markdown(f"""
                <div style="background: {bg_color}; padding: 15px; border-radius: 12px; border: 2px solid {border_color}; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1;">
                        <b style="font-size: 1.1rem; color: #1f2937;">{t['task']}</b><br>
                        <span style="color: #6b7280; font-size: 0.9rem;">⏰ {due_str}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🗑️ Remove", key=f"del_{i}"):
                # Find original index to pop properly
                original_index = st.session_state.tasks.index(t)
                st.session_state.tasks.pop(original_index)
                st.rerun()

        # Alarm Trigger
        if not t["alerted"] and now >= t["datetime"]:
            st.toast(f"🔔 ALERT: {t['task']} is due!", icon="⏰")
            st.warning(f"⏰ **TIME'S UP!** {t['task']}")
            st.balloons()
            # Audio Alert injection
            st.markdown("""
                <audio autoplay>
                    <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
                </audio>
            """, unsafe_allow_html=True)
            t["alerted"] = True
    st.markdown('</div>', unsafe_allow_html=True)

# Smart Auto-refresh: Only refresh if user is not currently typing/focusing an input
st.markdown("""
<script>
    setTimeout(function() {
        // Prevent reload if user is interacting with inputs
        if (!document.querySelector('input:focus, textarea:focus, select:focus')) {
            window.location.reload();
        } else {
            // Check again in 5 seconds if they ignore it
            console.log('Skipping auto-refresh due to user interaction');
        }
    }, 10000);
</script>
""", unsafe_allow_html=True)
