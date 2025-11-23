import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
import streamlit.components.v1 as components
import uuid

st.set_page_config(
    page_title="AI Interview Coach",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced system prompt with agentic behavior
SYSTEM_PROMPT = """You are an expert interview coach with 15+ years of experience. Your role is to:

1. CONDUCT REALISTIC INTERVIEWS:
   - Ask role-specific questions that real interviewers would ask
   - Ask intelligent follow-up questions based on candidate responses
   - Probe deeper when answers are vague or incomplete
   - Adapt difficulty based on candidate's experience level

2. BE CONVERSATIONALLY INTELLIGENT:
   - If candidate is confused, clarify and guide them
   - If candidate goes off-topic, gently redirect: "That's interesting, but let's focus on [topic]. Can you tell me..."
   - If candidate is nervous, be encouraging and supportive
   - If candidate gives short answers, ask: "Can you elaborate on that?" or "Tell me more about..."

3. MAINTAIN INTERVIEW FLOW:
   - Ask 1 question at a time
   - Keep responses concise (2-3 sentences per response)
   - Balance between technical and behavioral questions
   - Transition smoothly between topics

4. HANDLE EDGE CASES:
   - If response is irrelevant: "I appreciate that, but for this [role] position, I'd like to know about [specific skill]. Can you share..."
   - If candidate asks questions: Answer briefly, then redirect: "Good question! [Answer]. Now, back to you..."
   - If candidate seems stuck: Offer a hint or rephrase the question

5. END INTERVIEW NATURALLY:
   - After 5-8 questions, ask: "Do you have any questions for me?"
   - Then say: "Great! Let's wrap up. I'll provide feedback now."

Remember: Be professional yet friendly. Make candidates feel comfortable while maintaining interview standards."""

FEEDBACK_PROMPT = """Analyze the interview and provide detailed feedback in this structure:

**OVERALL PERFORMANCE: [Score/10]**

**STRENGTHS:**
- [List 2-3 specific things they did well with examples]

**AREAS FOR IMPROVEMENT:**
- [List 2-3 specific areas with actionable advice]

**COMMUNICATION SKILLS: [Score/10]**
- Clarity, structure, and articulation

**TECHNICAL KNOWLEDGE: [Score/10]** (if applicable)
- Depth and accuracy of technical responses

**BEHAVIORAL COMPETENCIES: [Score/10]**
- Examples, storytelling, STAR method usage

**KEY RECOMMENDATIONS:**
1. [Specific actionable tip]
2. [Specific actionable tip]
3. [Specific actionable tip]

Be constructive, specific, and encouraging."""

# Direct voice recorder that fills Streamlit text area
def voice_recorder_direct(text_area_key):
    """Voice recorder that directly fills the Streamlit text area"""
    unique_id = str(uuid.uuid4())[:8]
    
    voice_html = f"""
    <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%); border-radius: 12px; margin-bottom: 15px;">
        <button id="voiceBtn_{unique_id}" style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 35px;
            border-radius: 25px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        " onmouseover="this.style.transform='scale(1.05)'" 
           onmouseout="this.style.transform='scale(1)'">
            🎤 Click to Speak
        </button>
        <div id="status_{unique_id}" style="margin-top: 12px; font-size: 16px; font-weight: 600; color: #666; min-height: 25px;"></div>
    </div>
    
    <script>
        const button = document.getElementById('voiceBtn_{unique_id}');
        const status = document.getElementById('status_{unique_id}');
        let recognition;
        let isListening = false;
        
        // Check if browser supports speech recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            button.onclick = function() {{
                if (!isListening) {{
                    recognition.start();
                    isListening = true;
                    button.textContent = '🔴 Listening...';
                    button.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
                    button.style.animation = 'pulse 1.5s infinite';
                    status.textContent = '🎤 Speak now...';
                    status.style.color = '#f5576c';
                }}
            }};
            
            recognition.onresult = function(event) {{
                const text = event.results[0][0].transcript;
                
                // Find Streamlit text area and fill it
                const textArea = window.parent.document.querySelector('textarea[aria-label="Type your response here"]');
                if (textArea) {{
                    // Set value
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                    nativeInputValueSetter.call(textArea, text);
                    
                    // Trigger React events
                    const event = new Event('input', {{ bubbles: true }});
                    textArea.dispatchEvent(event);
                    
                    status.textContent = '✅ Text inserted! Click Send below.';
                    status.style.color = '#28a745';
                }} else {{
                    status.textContent = '⚠️ Could not find text box';
                    status.style.color = '#ffc107';
                }}
                
                isListening = false;
                button.textContent = '🎤 Click to Speak';
                button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                button.style.animation = 'none';
            }};
            
            recognition.onerror = function(event) {{
                status.textContent = '❌ Error: ' + event.error + '. Try again.';
                status.style.color = '#dc3545';
                isListening = false;
                button.textContent = '🎤 Click to Speak';
                button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                button.style.animation = 'none';
            }};
            
            recognition.onend = function() {{
                isListening = false;
                if (button.textContent === '🔴 Listening...') {{
                    button.textContent = '🎤 Click to Speak';
                    button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                    button.style.animation = 'none';
                }}
            }};
        }} else {{
            button.disabled = true;
            button.textContent = '❌ Voice Not Supported';
            button.style.backgroundColor = '#999';
            status.textContent = 'Use Chrome, Edge, or Safari';
            status.style.color = '#dc3545';
        }}
    </script>
    
    <style>
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
    </style>
    """
    components.html(voice_html, height=120)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "interview_active" not in st.session_state:
    st.session_state.interview_active = False
if "interview_ended" not in st.session_state:
    st.session_state.interview_ended = False
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "use_voice" not in st.session_state:
    st.session_state.use_voice = False
if "user_response" not in st.session_state:
    st.session_state.user_response = ""

# Sidebar
with st.sidebar:
    st.markdown("# Interview Coach")
    
    # API Key
    st.markdown("### 🔑 Setup")
    api_key = st.text_input(
        "Gemini API Key",
        value=st.session_state.api_key,
        type="password",
        help="Get free key: https://aistudio.google.com/app/apikey"
    )
    
    if api_key:
        st.session_state.api_key = api_key
        genai.configure(api_key=api_key)
        st.success("✅ Connected")
    else:
        st.warning("⚠️ API key required")
    
    # Voice toggle
    st.markdown("### 🎤 Voice Input")
    use_voice = st.checkbox("Enable Voice Input", value=st.session_state.use_voice)
    st.session_state.use_voice = use_voice
    
    if use_voice:
        st.info("💡 Click microphone → Speak → Text appears in box → Click Send!")
    
    st.markdown("---")
    
    # Stats
    if st.session_state.interview_active:
        st.markdown("### Interview Progress")
        st.metric("Questions Asked", st.session_state.question_count)
        
        if st.session_state.start_time:
            elapsed = (datetime.now() - st.session_state.start_time).seconds // 60
            st.metric("Duration", f"{elapsed} min")
        
        st.markdown("---")
        
        # End interview button
        if st.button("End Interview & Get Feedback", use_container_width=True, type="primary"):
            st.session_state.interview_ended = True
            st.rerun()
    
    # Reset button
    if st.session_state.interview_active or st.session_state.interview_ended:
        if st.button("🔄 Start New Interview", use_container_width=True):
            st.session_state.messages = []
            st.session_state.interview_active = False
            st.session_state.interview_ended = False
            st.session_state.question_count = 0
            st.session_state.start_time = None
            st.session_state.user_response = ""
            st.rerun()
    
    st.markdown("---")
    
    # Tips
    st.markdown("### 💡 Interview Tips")
    st.info("""
    **Best Practices:**
    - Use STAR method for behavioral questions
    - Be specific with examples
    - Show enthusiasm
    - Ask clarifying questions if needed
    """)
    
    st.markdown("---")
    st.markdown("### 📚 Resources")
    st.markdown("""
    - [STAR Method Guide](https://www.themuse.com/advice/star-interview-method)
    - [Common Questions](https://www.indeed.com/career-advice/interviewing/top-interview-questions-and-answers)
    """)

# Main content
st.title("AI Interview Practice Partner")
st.markdown("Practice interviews with an AI coach. Speak or type your answers!")

# API key check
if not st.session_state.api_key:
    st.warning("Please enter your Gemini API key in the sidebar to begin")
    with st.expander("How to get a FREE API key"):
        st.markdown("""
        1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Sign in with your Google account
        3. Click "Create API key"
        4. Copy and paste it in the sidebar
        
        **No credit card required!** 🎉
        """)
    st.stop()

# Interview setup (before starting)
if not st.session_state.interview_active and not st.session_state.interview_ended:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Select Role")
        role = st.selectbox(
            "What position are you interviewing for?",
            [
                "Software Engineer",
                "Data Scientist",
                "Product Manager",
                "Sales Representative",
                "Marketing Manager",
                "Retail Associate",
                "Customer Service",
                "DevOps Engineer",
                "UI/UX Designer",
                "Business Analyst"
            ]
        )
    
    with col2:
        st.markdown("### Experience Level")
        experience = st.radio(
            "Your experience level:",
            ["Entry Level (0-2 years)", "Mid Level (3-5 years)", "Senior Level (5+ years)"]
        )
    
    st.markdown("### Interview Focus (Optional)")
    focus_areas = st.multiselect(
        "Select specific areas to focus on:",
        ["Technical Skills", "Behavioral Questions", "Problem Solving", "Leadership", "Communication", "Past Projects"]
    )
    
    st.markdown("---")
    
    # Start button
    if st.button("Start Interview", use_container_width=True, type="primary"):
        focus_text = f"\nFocus on: {', '.join(focus_areas)}" if focus_areas else ""
        
        initial_message = f"""Starting mock interview for: {role} ({experience})
{focus_text}

Hello! I'm excited to interview you today for the {role} position. 

Let's start with a warm-up question: **Tell me about yourself and why you're interested in this role.**

Take your time, and feel free to ask if you need clarification on any question."""
        
        st.session_state.messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nRole: {role}\nExperience: {experience}{focus_text}"},
            {"role": "assistant", "content": initial_message}
        ]
        st.session_state.interview_active = True
        st.session_state.start_time = datetime.now()
        st.session_state.role = role
        st.session_state.experience = experience
        st.session_state.question_count = 1
        st.rerun()

# Interview in progress
elif st.session_state.interview_active and not st.session_state.interview_ended:
    # Display conversation
    for msg in st.session_state.messages[1:]:  # Skip system message
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
    
    st.markdown("---")
    
    # Voice input button (if enabled)
    if st.session_state.use_voice:
        voice_recorder_direct("response_input")
    
    # Text area for response
    user_input = st.text_area(
        "Type your response here",
        value=st.session_state.user_response,
        height=150,
        key="response_input",
        placeholder="Type your answer or use the microphone above to speak..."
    )
    
    # Send button
    col1, col2 = st.columns([3, 1])
    with col2:
        send_button = st.button("📤 Send", type="primary", use_container_width=True)
    
    if send_button and user_input.strip():
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.user_response = ""  # Clear input
        
        # Generate response
        with st.spinner("Thinking..."):
            try:
                model = genai.GenerativeModel(
                    'gemini-2.5-flash',
                    system_instruction=st.session_state.messages[0]["content"]
                )
                
                # Build chat history
                chat_history = []
                for msg in st.session_state.messages[1:-1]:
                    if msg["role"] == "user":
                        chat_history.append({"role": "user", "parts": [msg["content"]]})
                    elif msg["role"] == "assistant":
                        chat_history.append({"role": "model", "parts": [msg["content"]]})
                
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(user_input)
                reply = response.text
                
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                # Count questions (rough estimate)
                if "?" in reply:
                    st.session_state.question_count += 1
                
                st.rerun()
                
            except Exception as e:
                if "quota" in str(e).lower():
                    st.error("❌ API quota exceeded. Please try again later or create a new API key.")
                else:
                    st.error(f"❌ Error: {str(e)}")
                st.session_state.messages.pop()

# Generate feedback
elif st.session_state.interview_ended:
    st.markdown("## 📋 Interview Feedback")
    
    with st.spinner("Analyzing your interview performance..."):
        try:
            # Prepare conversation for analysis
            conversation = "\n\n".join([
                f"{'Interviewer' if msg['role'] == 'assistant' else 'Candidate'}: {msg['content']}"
                for msg in st.session_state.messages[1:]  # Skip system message
            ])
            
            feedback_model = genai.GenerativeModel('gemini-2.5-flash')
            feedback_response = feedback_model.generate_content(
                f"{FEEDBACK_PROMPT}\n\nInterview Transcript:\n{conversation}"
            )
            
            st.markdown(feedback_response.text)
            
            # Download transcript
            st.markdown("---")
            st.markdown("### 📥 Download Interview Transcript")
            
            transcript_data = {
                "role": st.session_state.role,
                "experience": st.session_state.experience,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "duration_minutes": (datetime.now() - st.session_state.start_time).seconds // 60,
                "conversation": [
                    {"speaker": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages[1:]
                ],
                "feedback": feedback_response.text
            }
            
            st.download_button(
                label="📄 Download Full Report (JSON)",
                data=json.dumps(transcript_data, indent=2),
                file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Error generating feedback: {str(e)}")