import streamlit as st
import matplotlib.pyplot as plt
import os
import sys
from dotenv import load_dotenv

# Ensure the project root is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent import app as agent_app

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="CPCoach - Competitive Programming Agent",
    page_icon="🎓",
    layout="wide"
)

# Custom premium styling
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #8892b0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .recommendation-card {
        background-color: #171923;
        border: 2px solid #2d3748;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        margin-bottom: 24px;
    }
    .problem-title {
        color: #63b3ed;
        font-size: 1.5rem;
        font-weight: 700;
        text-decoration: none;
        margin-bottom: 10px;
        display: inline-block;
    }
    .problem-title:hover {
        color: #3182ce;
        text-decoration: underline;
    }
    .rating-badge {
        background-color: #2b6cb0;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-right: 10px;
    }
    .tag-badge {
        background-color: #2d3748;
        color: #cbd5e0;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        display: inline-block;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .rationale-box {
        background-color: #1a202c;
        border-left: 4px solid #805ad5;
        padding: 12px 16px;
        border-radius: 4px;
        font-style: italic;
        color: #e2e8f0;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "handle": "",
        "csv_path": None,
        "force_offline": False,
        "submissions": [],
        "weak_tags": [],
        "target_ratings": {},
        "current_tag": None,
        "current_problem": None,
        "recommendation_rationale": None,
        "feedback": None,
        "history": [],
        "logs": [],
        "api_key": None
    }

# App Header
st.markdown("<div class='main-title'>CPCoach 🎓</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>A feedback-driven AI agent that analyzes your Codeforces weaknesses and coaches you to success.</div>", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Detect Groq API Key from environment
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        st.session_state.agent_state["api_key"] = groq_key
        st.caption("🟢 Groq API Key loaded from `.env`")
    else:
        st.session_state.agent_state["api_key"] = None
        st.caption("🟡 No Groq Key in `.env` (Template Mode)")
    
    # Input Handle
    handle = st.text_input("Codeforces Handle", value="tourist", help="Valid handle on Codeforces")
    st.session_state.agent_state["csv_path"] = None
    st.session_state.agent_state["handle"] = handle

    force_offline = st.checkbox("Force Offline Mode (Uses offline problem DB)", value=False)
    st.session_state.agent_state["force_offline"] = force_offline
    
    st.markdown("---")
    
    # Action buttons
    col_start, col_reset = st.columns(2)
    with col_start:
        if st.button("🚀 Run Analysis", use_container_width=True):
            # Clear past run state but keep config
            st.session_state.agent_state["submissions"] = []
            st.session_state.agent_state["weak_tags"] = []
            st.session_state.agent_state["current_tag"] = None
            st.session_state.agent_state["current_problem"] = None
            st.session_state.agent_state["recommendation_rationale"] = None
            st.session_state.agent_state["feedback"] = None
            st.session_state.agent_state["history"] = []
            st.session_state.agent_state["logs"] = ["[System] Initializing session."]
            st.session_state.agent_state["target_ratings"] = {}
            
            with st.spinner("Analyzing profile & finding recommendation..."):
                result = agent_app.invoke(st.session_state.agent_state)
                st.session_state.agent_state = result
                st.success("Analysis complete!")
                st.rerun()
                
    with col_reset:
        if st.button("🔄 Reset Session", use_container_width=True):
            st.session_state.agent_state = {
                "handle": "",
                "csv_path": None,
                "force_offline": False,
                "submissions": [],
                "weak_tags": [],
                "target_ratings": {},
                "current_tag": None,
                "current_problem": None,
                "recommendation_rationale": None,
                "feedback": None,
                "history": [],
                "logs": [],
                "api_key": None
            }
            st.rerun()

    # Log Debugger in Sidebar
    st.header("🐞 Agent Execution Logs")
    if st.session_state.agent_state.get("logs"):
        for log in reversed(st.session_state.agent_state["logs"]):
            st.caption(log)
    else:
        st.caption("No logs yet. Run analysis to start.")

# Main Dashboard Layout
state = st.session_state.agent_state

if not state.get("submissions"):
    st.info("👈 Enter your Codeforces handle or select the local CSV fallback, then click **Run Analysis** to begin!")
else:
    # 2-column layout: Left = Weaknesses, Right = Recommendation & History
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📊 Your Weakness Breakdown")
        
        weak_tags = state.get("weak_tags", [])
        if not weak_tags:
            st.write("No weakness scores calculated.")
        else:
            # Gather details of weaknesses
            # We want to map each weak tag to its score
            tags = [wt[0] for wt in weak_tags[:10]]
            scores = [wt[1] for wt in weak_tags[:10]]
            
            # Matplotlib bar chart
            fig, ax = plt.subplots(figsize=(6, 4))
            fig.patch.set_facecolor('#0e1117')
            ax.set_facecolor('#1a202c')
            
            # Indigo-Purple gradient mock-up using color list
            colors = plt.cm.plasma([0.3 + 0.5 * (i / len(tags)) for i in range(len(tags))])
            
            bars = ax.barh(tags[::-1], scores[::-1], color=colors)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#8892b0')
            ax.spines['bottom'].set_color('#8892b0')
            ax.tick_params(colors='#8892b0', labelsize=9)
            ax.set_xlabel("Weakness Score", color='#8892b0', fontsize=10)
            ax.set_title("Top Weak Topic Areas (Weighted by Attempts)", color='#ffffff', fontsize=12, fontweight='bold')
            
            # Adjust padding and render
            plt.tight_layout()
            st.pyplot(fig)
            
            # Display detailed stats table
            st.markdown("### 📈 Topic Stat Breakdown")
            
            # Calculate stats for display
            submissions = state.get("submissions", [])
            tag_stats = []
            for wt in weak_tags:
                tag_name = wt[0]
                weakness_score = wt[1]
                
                # Fetch attempts & solved count
                prob_attempts = set()
                prob_solves = set()
                for sub in submissions:
                    if tag_name in sub["tags"]:
                        prob_attempts.add(sub["problem_id"])
                        if sub["verdict"] == "OK":
                            prob_solves.add(sub["problem_id"])
                
                attempts_cnt = len(prob_attempts)
                solves_cnt = len(prob_solves)
                solve_rate = (solves_cnt / attempts_cnt) * 100 if attempts_cnt > 0 else 100.0
                
                tag_stats.append({
                    "Topic": tag_name,
                    "Attempts": attempts_cnt,
                    "Solved": solves_cnt,
                    "Solve Rate": f"{solve_rate:.1f}%",
                    "Weakness Score": f"{weakness_score:.3f}",
                    "Target Rating": state["target_ratings"].get(tag_name, "Not set")
                })
                
            st.table(tag_stats[:8])
            
    with col_right:
        st.subheader("🎯 Current Recommendation")
        
        prob = state.get("current_problem")
        tag = state.get("current_tag")
        rationale = state.get("recommendation_rationale")
        target_rating = state["target_ratings"].get(tag, 800) if tag else 800
        
        if not prob:
            st.warning("No problem recommended. All candidate problems in the dataset may have been solved, or no problems match.")
        else:
            # Display target rating card
            st.metric(
                label=f"Current Focus Area: {tag.capitalize() if tag else 'None'}", 
                value=f"Target Rating: {target_rating}",
                delta="Updated dynamic target rating" if state.get("history") else None
            )
            
            # HTML Card representing recommendation
            prob_url = f"https://codeforces.com/problemset/problem/{prob['contestId']}/{prob['index']}"
            
            st.markdown(f"""
            <div class="recommendation-card">
                <a href="{prob_url}" target="_blank" class="problem-title">
                    {prob['contestId']}{prob['index']} - {prob['name']} 🔗
                </a>
                <div>
                    <span class="rating-badge">Rating: {prob['rating']}</span>
                    {' '.join([f'<span class="tag-badge">{t}</span>' for t in prob['tags']])}
                </div>
                <div class="rationale-box">
                    <strong>Coach Rationale:</strong> "{rationale}"
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Feedback interaction
            st.write("💬 **Did you solve it?** Report back to coach:")
            col_pass, col_fail = st.columns(2)
            
            with col_pass:
                if st.button("✅ Solved (Pass)", type="primary", use_container_width=True):
                    # Set feedback and invoke agent
                    state["feedback"] = "pass"
                    with st.spinner("Processing solve... adjusting difficulty up"):
                        result = agent_app.invoke(state)
                        st.session_state.agent_state = result
                        st.rerun()
                        
            with col_fail:
                if st.button("❌ Stuck / Failed (Fail)", type="secondary", use_container_width=True):
                    state["feedback"] = "fail"
                    with st.spinner("Processing fail... adjusting difficulty down"):
                        result = agent_app.invoke(state)
                        st.session_state.agent_state = result
                        st.rerun()
                        
        # Recommendation History
        st.markdown("---")
        st.subheader("📜 Session Recommendation History")
        
        history = state.get("history", [])
        if not history:
            st.info("No recommendations attempted in this session yet.")
        else:
            for idx, item in enumerate(reversed(history)):
                p = item["problem"]
                verdict = item["verdict"]
                verdict_color = "🟢 PASS" if verdict == "pass" else "🔴 FAIL"
                p_url = f"https://codeforces.com/problemset/problem/{p['contestId']}/{p['index']}"
                
                st.markdown(
                    f"**Round {len(history) - idx}**: [{p['contestId']}{p['index']} - {p['name']}]({p_url}) "
                    f"| Tag: `{item['tag']}` | Target Rating: `{item['target_rating']}` | Result: **{verdict_color}**"
                )
