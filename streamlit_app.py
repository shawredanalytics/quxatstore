import streamlit as st
import os
import shutil
import base64
import urllib.parse
from datetime import datetime
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer

# Page config
st.set_page_config(
    page_title="QuXAT Healthcare Quality Systems Documents Repository",
    page_icon="📚",
    layout="wide"
)

# CSS for better mobile responsiveness and aesthetics
st.markdown("""
    <style>
        /* Global Styles */
        .stApp {
            background-color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #004d40; /* Teal 900 */
            font-weight: 600;
            text-align: center;
        }
        
        /* Center text for better aesthetics */
        .centered-text {
            text-align: center;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: #00796b; /* Teal 700 */
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #004d40;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            color: white;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #e0f2f1; /* Teal 50 */
            border-right: 1px solid #b2dfdb;
        }
        
        /* Inputs */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #b0bec5;
        }
        
        /* Dataframes */
        [data-testid="stDataFrame"] {
            border: 1px solid #cfd8dc;
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Cards/Containers */
        div.stInfo, div.stSuccess, div.stWarning, div.stError {
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border: none;
        }
        
        /* Custom Container for Search Results */
        .search-result-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        [data-testid="stColumn"] {
            min-width: 0px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Constants
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Helper functions
def get_logo_path():
    for ext in ["png", "jpg", "jpeg", "svg", "webp"]:
        possible_path = os.path.join("assets", f"logo.{ext}")
        if os.path.exists(possible_path):
            return possible_path
    return None

logo_path = get_logo_path()

def save_file(uploaded_file):
    if uploaded_file is not None:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

def get_files():
    files = []
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            if filename != ".gitkeep":
                file_path = os.path.join(UPLOAD_DIR, filename)
                stats = os.stat(file_path)
                files.append({
                    "Filename": filename,
                    "Size (KB)": round(stats.st_size / 1024, 2),
                    "Upload Date": datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
    return files

# Sidebar for navigation
with st.sidebar:
    page = st.selectbox("Navigation", ["Document Search", "Admin Upload"])
    st.markdown("---")
    st.markdown("### About QuXAT")
    st.info(
        "QuXAT Healthcare Quality Systems Documents Repository is a secure, centralized digital platform designed to help healthcare organizations efficiently access quality, safety and related compliance documents. "
        "The portal helps healthcare organizations to prepare for accreditation and regulatory requirements (such as NABL, NABH, ISO, and other healthcare standards), QuXAT ensures easy access to basic structured documentation with version control. "
        "Organizations can download resources and modify them as per their internal requirements."
    )
    st.link_button("Visit QuXAT Website", "https://www.quxat.com")
    
    st.markdown("---")
    
    # Stay Connected
    st.markdown("### Stay Connected")
    
    # Subscribe
    st.caption("Subscribe for updates regarding QuXAT Healthcare Quality Systems Documents Repository")
    email = st.text_input("Enter your email address")
    if st.button("Subscribe"):
        if email and "@" in email: # Basic validation
            with open("subscribers.txt", "a") as f:
                f.write(f"{email},{datetime.now()}\n")
            st.success("Subscribed successfully!")
        elif not email:
            st.warning("Please enter an email address.")
        else:
            st.warning("Please enter a valid email address.")
            
    # Share
    st.caption("Share QuXAT Healthcare Quality Systems Documents Repository via Email")
    subject = "QuXAT Healthcare Quality Systems Documentation Repository"
    body = """Dear Team,

Greetings from QuXAT.

We are pleased to introduce the QuXAT Healthcare Quality Systems Documents Repository, a secure and centralized digital platform designed to support healthcare organizations in efficiently accessing quality, safety, and compliance-related documentation.

The repository is developed to assist organizations in preparing for accreditation and regulatory requirements, including NABL, NABH, ISO, and other recognized healthcare standards. QuXAT provides basic, structured documentation with version control, ensuring clarity, consistency, and ease of use.

Key features of the QuXAT Healthcare Quality Systems Documents Repository:
* Centralized access to quality and compliance documents
* Structured formats aligned with healthcare accreditation standards
* Version-controlled documents for better governance
* Downloadable resources that can be customized as per internal organizational requirements

Healthcare organizations can freely download the documents and modify them to suit their operational and compliance needs.

Free Access:
https://quxatstore.streamlit.app/

We hope the QuXAT Healthcare Quality Systems Documents Repository will support your organization in strengthening quality systems and simplifying accreditation preparedness.

For any queries or support, please feel free to reach out.

Warm regards,
Team QuXAT"""
    subject_encoded = urllib.parse.quote(subject)
    body_encoded = urllib.parse.quote(body)
    mailto_link = f"mailto:?subject={subject_encoded}&body={body_encoded}"
    st.link_button("Share via Email 📧", mailto_link)
    
    st.markdown("---")
    
    # Support
    st.markdown("### QuXAT Healthcare Quality Systems Documents Repository Support")
    st.markdown("Need help? Connect with our support team!")
    
    whatsapp_url = "https://wa.me/916301237212"
    
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 10px;">
            <a href="{whatsapp_url}" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="40" alt="WhatsApp">
            </a>
            <a href="{whatsapp_url}" target="_blank" style="text-decoration: none; color: inherit; font-weight: bold;">
                +91 6301237212
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.markdown("© 2025 QuXAT - All Rights Reserved.")

# Title
if logo_path:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image(logo_path, width=350)
st.title("QuXAT Healthcare Quality Systems Documents Repository")
st.markdown("<h2 style='text-align: center; color: #2e7d32;'>✅ Free Access for all Healthcare Professionals</h2>", unsafe_allow_html=True)
st.subheader("Repository for Healthcare Quality & Compliance Documentation")
st.markdown("<p style='text-align: center;'>Access essential resources for NABL, NABH, ISO, and other healthcare accreditation standards.</p>", unsafe_allow_html=True)

# WhatsApp Support Section (Below Hero)
st.markdown("### 📞 QuXAT Healthcare Quality Systems Documents Repository Support")
whatsapp_url = "https://wa.me/916301237212"
st.markdown(
    f"""
    <div style="display: flex; justify-content: center; align-items: center; gap: 10px;">
        <a href="{whatsapp_url}" target="_blank">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="35" alt="WhatsApp">
        </a>
        <a href="{whatsapp_url}" target="_blank" style="text-decoration: none; color: inherit; font-size: 1.1em;">
            Connect with us on WhatsApp: <strong>+91 6301237212</strong>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

if page == "Document Search":
    st.header("Search Healthcare Documents")
    st.markdown("Find SOPs, manuals, checklists, and forms for accreditation.")
    
    # Search bar container
    with st.container():
        # Search bar
        search_query = st.text_input(
            "🔍 Enter keywords to find documents:",
            placeholder="e.g., NABL SOP, Infection Control Manual, Fire Safety Form...",
            help="Type document names or keywords to filter the list."
        )
    
    # Get files
    files = get_files()
    
    if files:
        df = pd.DataFrame(files)
        
        # Filter if search query exists
        if search_query:
            df = df[df['Filename'].str.contains(search_query, case=False)]
        
        if not df.empty:
            # Display files
            df_display = df.reset_index(drop=True)
            df_display.index = df_display.index + 1
            st.dataframe(df_display, use_container_width=True)
            
            # View & Download section
            st.subheader("View & Download")
            selected_file = st.selectbox("Select a file to view/download", df['Filename'])
            
            if selected_file:
                file_path = os.path.join(UPLOAD_DIR, selected_file)
                
                # Download Button
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    st.download_button(
                        label=f"Download {selected_file}",
                        data=file_data,
                        file_name=selected_file,
                        mime="application/octet-stream"
                    )
                
                # Preview Logic
                st.markdown("---")
                st.subheader("Document Preview")
                
                file_extension = os.path.splitext(selected_file)[1].lower()
                
                try:
                    if file_extension == ".pdf":
                        with open(file_path, "rb") as f:
                            pdf_data = f.read()
                        pdf_viewer(input=pdf_data)
                    
                    elif file_extension in [".png", ".jpg", ".jpeg"]:
                        st.image(file_path)
                        
                    elif file_extension in [".csv"]:
                        df_preview = pd.read_csv(file_path)
                        st.dataframe(df_preview)
                        
                    elif file_extension in [".xlsx", ".xls"]:
                        df_preview = pd.read_excel(file_path)
                        st.dataframe(df_preview)
                        
                    elif file_extension in [".txt", ".md", ".py", ".json", ".js", ".html", ".css"]:
                        with open(file_path, "r", encoding="utf-8") as f:
                            st.text(f.read())
                    else:
                        st.info(f"Preview not available for {file_extension} files. Please download to view.")
                except Exception as e:
                    st.error(f"Error previewing file: {str(e)}")
        else:
            st.info("No documents found matching your search.")
    else:
        st.info("No documents uploaded yet.")

elif page == "Admin Upload":
    if logo_path:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(logo_path, width=80)
        with col2:
            st.header("Admin Upload")
    else:
        st.header("Admin Upload")
    
    # Password protection (simple)
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == "admin123":  # Simple password for demo
        uploaded_file = st.file_uploader("Choose a file", accept_multiple_files=False)
        
        if uploaded_file is not None:
            if st.button("Upload Document"):
                file_path = save_file(uploaded_file)
                if file_path:
                    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                else:
                    st.error("Failed to upload file.")
                    
        # File Management
        st.markdown("---")
        st.subheader("Current Repository Content")
        files = get_files()
        
        if files:
            # Display list of files
            df = pd.DataFrame(files)
            df_display = df.reset_index(drop=True)
            df_display.index = df_display.index + 1
            st.dataframe(df_display, use_container_width=True)
            
            st.markdown("### Delete Files")
            file_to_delete = st.selectbox("Select file to delete", [f['Filename'] for f in files])
            if st.button("Delete File"):
                os.remove(os.path.join(UPLOAD_DIR, file_to_delete))
                st.success(f"File '{file_to_delete}' deleted!")
                st.rerun()
        else:
            st.info("No documents uploaded yet.")
    else:
        if password:
            st.error("Incorrect password")
