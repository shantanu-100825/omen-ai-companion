import streamlit as st
from omen.agent import OmenAgent
from omen.memory import MemoryStore
from omen.voice import transcribe_audio, speak_text, voice_status
from omen.config import OLLAMA_MODEL, CLOUD_MODEL, PROVIDER_MODE

st.set_page_config(page_title="OMEN AI V2", page_icon="◈", layout="wide")
st.markdown("""
<style>
.stApp {background: #0b1020; color: #edf2ff;}
[data-testid="stSidebar"] {background: #111a30;}
.omen-title {font-size: 2.45rem; font-weight: 850; letter-spacing: .14em; color: #a8c7ff;}
.omen-sub {color: #91a4c8; margin-top: -12px;}
[data-testid="stChatMessage"] {border: 1px solid #263654; border-radius: 14px; padding: 10px;}
div.stButton > button {border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

memory = MemoryStore()
agent = OmenAgent(memory)

with st.sidebar:
    st.markdown("## ◈ OMEN CONTROL")
    st.caption("V2 · Hybrid intelligence · Voice-first")
    st.markdown(f"**Mode:** `{PROVIDER_MODE}`")
    st.markdown(f"**Local model:** `{OLLAMA_MODEL}`")
    st.markdown(f"**Cloud model:** `{CLOUD_MODEL}`")
    st.divider()
    st.markdown("### Voice status")
    st.write(voice_status())
    st.caption("Speech recognition runs locally when faster-whisper is installed. Speech synthesis uses an online TTS service.")
    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.button("Show saved memories", use_container_width=True):
        st.session_state.show_memory = not st.session_state.get("show_memory", False)
    st.divider()
    st.markdown("**Quick commands**")
    examples = [
        "Introduce yourself, Omen.",
        "Calculate 125 * (48 + 12).",
        "Remember that my project is called Orion.",
        "Search my memory for Orion.",
        "Explain agentic AI in Marathi.",
    ]
    for i, prompt in enumerate(examples):
        if st.button(prompt, key=f"example_{i}", use_container_width=True):
            st.session_state.pending_prompt = prompt

st.markdown('<div class="omen-title">◈ OMEN AI</div>', unsafe_allow_html=True)
st.markdown('<div class="omen-sub">Your voice-first personal AI agent</div>', unsafe_allow_html=True)
st.write("Talk to Omen, type a task, or let it use its tools.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_memory" not in st.session_state:
    st.session_state.show_memory = False

if st.session_state.show_memory:
    with st.expander("Persistent memory", expanded=True):
        notes = memory.list_notes()
        if notes:
            for note in notes:
                st.markdown(f"- **{note['created_at']}** — {note['content']}")
        else:
            st.info("No saved memories yet.")

st.markdown("### Speak to OMEN")
audio_value = st.audio_input("Record your message", key="omen_voice_input")
voice_col1, voice_col2 = st.columns([1, 2])
with voice_col1:
    transcribe_clicked = st.button("Transcribe recording", disabled=audio_value is None, use_container_width=True)
with voice_col2:
    st.caption("Record, then select Transcribe. Review the recognized text before sending it.")

if transcribe_clicked and audio_value is not None:
    with st.spinner("Recognizing speech locally..."):
        try:
            st.session_state.voice_draft = transcribe_audio(audio_value.getvalue())
        except Exception as exc:
            st.error(str(exc))

if "voice_draft" in st.session_state:
    draft = st.text_area("Recognized speech — edit before sending", key="voice_draft_editor",
                         value=st.session_state.voice_draft, height=90)
    if st.button("Send voice message", type="primary", disabled=not draft.strip()):
        st.session_state.pending_prompt = draft.strip()
        st.session_state.pop("voice_draft", None)
        st.rerun()

st.divider()
st.markdown("### Conversation")
for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])

prompt = st.session_state.pop("pending_prompt", None) or st.chat_input("Message or ask OMEN to do something...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("OMEN is thinking..."):
            try:
                answer, trace, provider_used = agent.run(st.session_state.messages)
                st.markdown(answer)
                st.caption(f"Brain used: {provider_used}")
                if trace:
                    with st.expander("Agent activity"):
                        for event in trace:
                            st.markdown(f"- {event}")
                st.session_state.last_answer = answer
            except Exception as exc:
                answer = f"OMEN couldn't complete the request: `{exc}`"
                st.error(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

if st.session_state.get("last_answer"):
    if st.button("🔊 Speak last response"):
        try:
            with st.spinner("Preparing voice response..."):
                audio_bytes = speak_text(st.session_state.last_answer)
            st.audio(audio_bytes, format="audio/mp3")
        except Exception as exc:
            st.error(f"Voice output is unavailable: {exc}")
