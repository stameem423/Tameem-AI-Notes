import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from PIL import Image
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Syed Tameem Ashraf's Note Maker", page_icon="📚", layout="wide")

# --- CUSTOM AESTHETIC STYLING (CSS) ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(to bottom right, #fdfbfb, #ebedee);
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #6C63FF;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #574bdf;
        transform: scale(1.02);
    }
    h1 {
        color: #2E3192;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .css-10trblm {
        color: #6C63FF;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER SECTION ---
col1, col2 = st.columns([1, 4])
with col1:
    st.write("") # Spacer
with col2:
    st.title("✨ AI Textbook Note Architect")
    st.markdown(f"**Developed by:** :blue[{'Syed Tameem Ashraf'}]")
    st.write("Transform messy textbooks into beautiful, structured study guides.")

st.divider()

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Setup")
    api_key = st.text_input("Enter Gemini API Key", type="password", help="Get your key at aistudio.google.com")
    st.divider()
    st.markdown("### 📝 Note Preferences")
    note_depth = st.select_slider("Detail Level", options=["Summary", "Detailed", "Mastery"])
    st.info("Ensure your images are clear for the best OCR results.")

# --- APP LOGIC ---
if not api_key:
    st.warning("👋 Please enter your API Key in the sidebar to start!")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3-flash-preview')

    # Upload Section with nice UI
    uploaded_files = st.file_uploader(
        "📂 Drop your textbook PDF or images here", 
        type=["pdf", "png", "jpg", "jpeg"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"Captured {len(uploaded_files)} files!")
        
        if st.button("🪄 Craft My Notes"):
            with st.status("Reading textbook pages...", expanded=True) as status:
                # Process images
                processed_images = []
                for file in uploaded_files:
                    if file.type == "application/pdf":
                        doc = fitz.open(stream=file.read(), filetype="pdf")
                        for page in doc:
                            pix = page.get_pixmap()
                            img = Image.open(io.BytesIO(pix.tobytes()))
                            processed_images.append(img)
                    else:
                        img = Image.open(file)
                        processed_images.append(img)
                
                status.update(label="Analyzing content with AI...", state="running")
                
                # AI Prompt
                prompt = f"""
                Act as a world-class academic researcher. Create {note_depth} level notes from these images.
                Structure the output as follows:
                1. Main Topic Heading
                2. Executive Summary
                3. Detailed Concepts (use bolding and bullet points)
                4. Visual Descriptions: If there are diagrams, explain them clearly.
                5. Review Questions: 3 questions to test my knowledge.
                """
                
                response = model.generate_content([prompt] + processed_images)
                status.update(label="Notes Ready!", state="complete", expanded=False)

            # Displaying Result in a nice box
            st.markdown("---")
            st.subheader("📖 Generated Study Guide")
            st.container(border=True).markdown(response.text)
            
            # Action Buttons
            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button("📥 Download as TXT", response.text, file_name="Ashraf_Notes.txt")
            with col_b:
                if st.button("🔄 Clear and Start Over"):
                    st.rerun()

# --- FOOTER ---
st.markdown("<br><hr><center>Made with ❤️ for learning by Syed Tameem Ashraf</center>", unsafe_allow_html=True)