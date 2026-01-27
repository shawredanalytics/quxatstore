import streamlit as st
import os
import shutil
import base64
import urllib.parse
from datetime import datetime
import pandas as pd
import json
from streamlit_pdf_viewer import pdf_viewer
from github import Github, GithubException

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

METADATA_FILE = os.path.join(UPLOAD_DIR, "metadata.json")
DRIVE_LINKS_FILE = os.path.join(UPLOAD_DIR, "drive_links.json")

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def update_metadata(filename, doc_type):
    metadata = load_metadata()
    metadata[filename] = doc_type
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=4)
    return METADATA_FILE

def load_drive_links():
    if os.path.exists(DRIVE_LINKS_FILE):
        with open(DRIVE_LINKS_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def add_drive_link(name, doc_type, url, description):
    links = load_drive_links()
    links.append(
        {
            "Name": name,
            "Type": doc_type,
            "URL": url,
            "Description": description,
        }
    )
    with open(DRIVE_LINKS_FILE, "w") as f:
        json.dump(links, f, indent=4)
    return DRIVE_LINKS_FILE

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

def upload_to_github(file_path, file_name):
    """
    Uploads a file to the GitHub repository.
    Requires 'GITHUB_TOKEN' in st.secrets.
    """
    try:
        if "GITHUB_TOKEN" not in st.secrets:
            return False, "GitHub token not found in secrets. Backup disabled."

        token = st.secrets["GITHUB_TOKEN"]
        g = Github(token)
        
        # Get the repo
        repo_name = "shawredanalytics/quxatstore" 
        repo = g.get_repo(repo_name)
        
        # Path in the repo
        repo_path = f"uploads/{file_name}"
        
        # Read the file content
        with open(file_path, "rb") as f:
            content = f.read()
            
        # Check if file exists to update or create
        try:
            contents = repo.get_contents(repo_path)
            # Update
            repo.update_file(contents.path, f"Update {file_name}", content, contents.sha)
            return True, f"File updated in GitHub repository: {repo_name}"
        except GithubException as e:
            if e.status == 404:
                # Create
                repo.create_file(repo_path, f"Add {file_name}", content)
                return True, f"File created in GitHub repository: {repo_name}"
            else:
                raise e
                
    except Exception as e:
        return False, f"GitHub upload failed: {str(e)}"

@st.cache_resource
def sync_from_github():
    """
    Syncs files from GitHub repository 'uploads' folder to local 'uploads' directory.
    Run once per session start.
    """
    try:
        if "GITHUB_TOKEN" not in st.secrets:
            print("GitHub token not found in secrets. Sync disabled.")
            return

        token = st.secrets["GITHUB_TOKEN"]
        g = Github(token)
        repo_name = "shawredanalytics/quxatstore"
        repo = g.get_repo(repo_name)
        
        try:
            contents = repo.get_contents("uploads")
            if not isinstance(contents, list):
                contents = [contents]
                
            for content_file in contents:
                if content_file.name == ".gitkeep":
                    continue
                    
                local_path = os.path.join(UPLOAD_DIR, content_file.name)
                
                if not os.path.exists(local_path) or content_file.name in ["metadata.json", "drive_links.json"]:
                    file_content = content_file.decoded_content
                    with open(local_path, "wb") as f:
                        f.write(file_content)
                    print(f"Downloaded {content_file.name} from GitHub.")
                    
        except GithubException as e:
            if e.status == 404:
                print("No uploads directory found in GitHub.")
            else:
                print(f"Error accessing GitHub uploads: {e}")
                
    except Exception as e:
        print(f"GitHub sync failed: {str(e)}")

# Run sync on startup
sync_from_github()

def get_files():
    metadata = load_metadata()
    files = []
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            if filename not in [".gitkeep", "metadata.json", "drive_links.json"]:
                file_path = os.path.join(UPLOAD_DIR, filename)
                stats = os.stat(file_path)
                files.append(
                    {
                        "Filename": filename,
                        "Type": metadata.get(filename, "General"),
                        "Size (KB)": round(stats.st_size / 1024, 2),
                        "Upload Date": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
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
    st.header("Search Healthcare Quality Systems Documents")
    st.markdown("Find SOPs, manuals, checklists, and forms for accreditation.")
    
    with st.container():
        search_query = st.text_input(
            "🔍 Enter keywords to find documents:",
            placeholder="e.g., NABL SOP, Infection Control Manual, Fire Safety Form...",
            help="Type document names or keywords to filter the list.",
        )
    
    files = get_files()
    drive_links = load_drive_links()
    
    all_types = set()
    for f in files:
        doc_type = f.get("Type")
        if doc_type:
            all_types.add(doc_type)
    for link in drive_links:
        doc_type = link.get("Type")
        if doc_type:
            all_types.add(doc_type)
    
    selected_types = []
    if all_types:
        selected_types = st.multiselect("Filter by Document Type", sorted(list(all_types)))
    
    if not files and not drive_links:
        st.info("No documents available yet.")
    else:
        if files:
            df = pd.DataFrame(files)
            
            if selected_types:
                df = df[df["Type"].isin(selected_types)]
            
            if search_query:
                df = df[df["Filename"].str.contains(search_query, case=False)]
            
            if not df.empty:
                df_display = df.reset_index(drop=True)
                df_display.index = df_display.index + 1
                st.dataframe(df_display, use_container_width=True)
                
                st.subheader("View & Download Local Documents")
                selected_file = st.selectbox("Select a local file to view/download", df["Filename"])
                
                if selected_file:
                    file_path = os.path.join(UPLOAD_DIR, selected_file)
                    
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                        st.download_button(
                            label=f"Download {selected_file}",
                            data=file_data,
                            file_name=selected_file,
                            mime="application/octet-stream",
                        )
                    
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
                st.info("No local documents found matching your search.")
        else:
            st.info("No local documents uploaded yet.")
        
        if drive_links:
            df_drive = pd.DataFrame(drive_links)
            
            if selected_types and "Type" in df_drive.columns:
                df_drive = df_drive[df_drive["Type"].isin(selected_types)]
            
            if search_query and "Name" in df_drive.columns:
                name_match = df_drive["Name"].str.contains(search_query, case=False)
                if "Description" in df_drive.columns:
                    desc_match = df_drive["Description"].fillna("").str.contains(search_query, case=False)
                    mask = name_match | desc_match
                else:
                    mask = name_match
                df_drive = df_drive[mask]
            
            if not df_drive.empty:
                st.markdown("---")
                st.subheader("Google Drive Documents")
                df_drive_display = df_drive.reset_index(drop=True)
                df_drive_display.index = df_drive_display.index + 1
                st.dataframe(df_drive_display, use_container_width=True)
                
                selected_drive = st.selectbox("Select a Google Drive document to open", df_drive["Name"])
                if selected_drive:
                    row = df_drive[df_drive["Name"] == selected_drive].iloc[0]
                    st.link_button(f"Open in Google Drive: {selected_drive}", row["URL"])
            else:
                st.info("No Google Drive documents found matching your search.")
        else:
            st.info("No Google Drive links added yet.")

elif page == "Admin Upload":
    if logo_path:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(logo_path, width=80)
        with col2:
            st.header("Admin Upload")
    else:
        st.header("Admin Upload")
    
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == "admin123":  # Simple password for demo
        uploaded_file = st.file_uploader("Choose a file", accept_multiple_files=False)
        doc_type = st.selectbox("Select Document Type", ["SOP", "Manual", "Forms", "Registers", "Work Instructions", "Posters"])
        
        if uploaded_file is not None:
            if st.button("Upload Document"):
                file_path = save_file(uploaded_file)
                if file_path:
                    # Update metadata
                    update_metadata(uploaded_file.name, doc_type)
                    
                    st.success(f"File '{uploaded_file.name}' saved locally!")
                    
                    # Backup to GitHub
                    with st.spinner("Backing up to GitHub..."):
                        # Upload file
                        success, message = upload_to_github(file_path, uploaded_file.name)
                        
                        # Upload metadata
                        meta_success, meta_msg = upload_to_github(METADATA_FILE, "metadata.json")
                        
                        if success:
                            st.success(message)
                        else:
                            st.warning(message)
                else:
                    st.error("Failed to save file locally.")
                    
        st.markdown("---")
        st.subheader("Current Repository Content")
        files = get_files()
        
        if files:
            df = pd.DataFrame(files)
            df_display = df.reset_index(drop=True)
            df_display.index = df_display.index + 1
            st.dataframe(df_display, use_container_width=True)
            
            st.markdown("### Delete Files")
            file_to_delete = st.selectbox("Select file to delete", [f["Filename"] for f in files])
            if st.button("Delete File"):
                os.remove(os.path.join(UPLOAD_DIR, file_to_delete))
                st.success(f"File '{file_to_delete}' deleted!")
                st.rerun()
        else:
            st.info("No documents uploaded yet.")
        
        st.markdown("---")
        st.subheader("Manage Google Drive Links")
        
        drive_name = st.text_input("Google Drive Document Name")
        drive_url = st.text_input("Google Drive URL")
        drive_type = st.selectbox(
            "Document Type for Google Drive Link",
            ["SOP", "Manual", "Forms", "Registers", "Work Instructions", "Posters"],
        )
        drive_description = st.text_area("Short Description (optional)", "")
        
        if st.button("Add Google Drive Link"):
            if drive_name and drive_url:
                drive_path = add_drive_link(drive_name, drive_type, drive_url, drive_description)
                st.success("Google Drive link added.")
                with st.spinner("Syncing Google Drive links to GitHub..."):
                    link_success, link_msg = upload_to_github(drive_path, "drive_links.json")
                    if link_success:
                        st.success(link_msg)
                    else:
                        st.warning(link_msg)
            else:
                st.warning("Please enter both document name and Google Drive URL.")
        
        drive_links_admin = load_drive_links()
        if drive_links_admin:
            df_drive_admin = pd.DataFrame(drive_links_admin)
            df_drive_admin_display = df_drive_admin.reset_index(drop=True)
            df_drive_admin_display.index = df_drive_admin_display.index + 1
            st.dataframe(df_drive_admin_display, use_container_width=True)
    else:
        if password:
            st.error("Incorrect password")
