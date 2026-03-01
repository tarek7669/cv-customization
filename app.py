"""
CV Customization Streamlit Application
"""

import os
import streamlit as st
from dotenv import load_dotenv
from cv_customizer import customize_cv, extract_company_name

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="CV Customizer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📄 CV Customizer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Tailor your CV to match job descriptions using AI - honestly and effectively</p>', unsafe_allow_html=True)

# Sidebar with instructions
with st.sidebar:
    st.header("ℹ️ How it works")
    
    st.markdown("""
    1. Paste your LaTeX CV
    2. Add the job description
    3. Click 'Customize CV'
    4. Download your tailored CV
    
    ---
    
    ### 💡 What the AI does
    - **Uncomments** relevant hidden content
    - **Comments out** irrelevant items (never deletes)
    - **Rewords** to match job terminology
    - **Reorders** for maximum impact
    - Optimizes for 2 pages
    
    ### ⚠️ Honesty guarantee
    The AI will **never fabricate** skills or experience.
    It only works with what's already in your CV.
    """)

# Main content - two columns for input
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Your LaTeX CV")
    latex_cv = st.text_area(
        "Paste your complete LaTeX CV code here",
        height=400,
        placeholder=r"""\documentclass[11pt,a4paper]{article}
\usepackage{...}

\begin{document}

% Your CV content here...

\end{document}""",
        label_visibility="collapsed"
    )

with col2:
    st.subheader("💼 Job Description")
    job_description = st.text_area(
        "Paste the target job description here",
        height=400,
        placeholder="""Job Title: Software Engineer

About the role:
We are looking for...

Requirements:
- 3+ years of experience in...
- Proficiency in...

Nice to have:
- Experience with...""",
        label_visibility="collapsed"
    )

# Generate button
st.divider()

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    generate_button = st.button(
        "✨ Customize CV",
        type="primary",
        use_container_width=True
    )

# Processing and output
if generate_button:
    # Validation
    if not latex_cv.strip():
        st.error("⚠️ Please paste your LaTeX CV.")
    elif not job_description.strip():
        st.error("⚠️ Please paste the job description.")
    elif not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OPENAI_API_KEY not found in .env file. Please add it.")
    else:
        # Process the CV
        with st.spinner("🔄 Customizing your CV... This may take a minute."):
            try:
                customized_cv = customize_cv(
                    latex_cv=latex_cv,
                    job_description=job_description
                )
                company_name = extract_company_name(job_description)
                
                # Store in session state
                st.session_state['customized_cv'] = customized_cv
                st.session_state['company_name'] = company_name
                st.success(f"✅ CV customized for **{company_name.replace('_', ' ').title()}**!")
                
            except ValueError as e:
                st.error(f"⚠️ Validation error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Display results if available
if 'customized_cv' in st.session_state:
    st.divider()
    st.subheader("📄 Customized CV")
    
    # Download button
    col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 1])
    with col_dl2:
        company = st.session_state.get('company_name', 'company')
        st.download_button(
            label=f"⬇️ Download {company}.tex",
            data=st.session_state['customized_cv'],
            file_name=f"{company}.tex",
            mime="application/x-tex",
            use_container_width=True
        )
    
    # Display the customized CV
    st.code(st.session_state['customized_cv'], language="latex")
    
    # Option to clear
    if st.button("🗑️ Clear Results"):
        del st.session_state['customized_cv']
        st.session_state.pop('company_name', None)
        st.rerun()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.85rem;">
    <p>💡 <strong>Tip:</strong> Review the customized CV carefully before using it. 
    The AI optimizes presentation but you know your experience best.</p>
</div>
""", unsafe_allow_html=True)
