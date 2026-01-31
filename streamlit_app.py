import streamlit as st
import os
import shutil
import base64
import urllib.parse
from datetime import datetime
import pandas as pd
import json
import random
import string
from streamlit_pdf_viewer import pdf_viewer
from github import Github, GithubException

# Page config
st.set_page_config(
    page_title="QuXAT Healthcare Repository",
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

def generate_quxat_code():
    """Generates a unique code starting with QUXAT followed by 6 alphanumeric characters."""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=6))
    return f"QUXAT{suffix}"

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
    # Check if entry exists to preserve code, or create new
    current_entry = metadata.get(filename)
    
    code = generate_quxat_code()
    if isinstance(current_entry, dict) and "code" in current_entry:
        code = current_entry["code"]
    elif isinstance(current_entry, str):
         # Migration case if hitting this function
         pass
         
    metadata[filename] = {
        "type": doc_type,
        "code": code
    }
    
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

def save_drive_links(links):
    with open(DRIVE_LINKS_FILE, "w") as f:
        json.dump(links, f, indent=4)
    return DRIVE_LINKS_FILE


@st.dialog("Document Preview", width="large")
def preview_document_modal(file_path, file_name):
    """
    Displays the document preview in a modal dialog.
    """
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"### {file_name}")
    with col2:
        try:
            with open(file_path, "rb") as f:
                file_data = f.read()
            st.download_button(
                label="⬇️ Download",
                data=file_data,
                file_name=file_name,
                mime="application/octet-stream",
                key="modal_download_btn"
            )
        except Exception:
            pass # Ignore if file read fails for download button
    
    file_ext = os.path.splitext(file_name)[1].lower()
    
    try:
        if file_ext == ".pdf":
             with open(file_path, "rb") as f:
                 pdf_data = f.read()
             pdf_viewer(input=pdf_data)
        
        elif file_ext in [".png", ".jpg", ".jpeg"]:
             st.image(file_path, use_container_width=True)
             
        elif file_ext in [".csv"]:
             df_preview = pd.read_csv(file_path)
             st.dataframe(df_preview, use_container_width=True)
             
        elif file_ext in [".xlsx", ".xls"]:
             df_preview = pd.read_excel(file_path)
             st.dataframe(df_preview, use_container_width=True)
             
        elif file_ext in [".txt", ".md", ".py", ".json", ".js", ".html", ".css"]:
             with open(file_path, "r", encoding="utf-8") as f:
                 st.text(f.read())
        else:
             st.info(f"Preview not available for {file_extension} files. Please download to view.")
    except Exception as e:
        st.error(f"Error previewing file: {str(e)}")

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

def get_github_token():
    """
    Retrieve GitHub token from secrets or local file fallback.
    """
    if "GITHUB_TOKEN" in st.secrets:
        return st.secrets["GITHUB_TOKEN"]
    
    # Fallback: Try to read .streamlit/secrets.toml relative to this script
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        secrets_path = os.path.join(current_dir, ".streamlit", "secrets.toml")
        if os.path.exists(secrets_path):
            with open(secrets_path, "r") as f:
                for line in f:
                    if "GITHUB_TOKEN" in line:
                        # Simple parsing for TOML line: KEY = "VALUE"
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            token = parts[1].strip().strip('"').strip("'")
                            if token:
                                return token
    except Exception as e:
        print(f"Error reading secrets manually: {e}")
    
    return None

def upload_to_github(file_path, file_name):
    """
    Uploads a file to the GitHub repository.
    Requires 'GITHUB_TOKEN' in st.secrets.
    """
    try:
        token = get_github_token()
        if not token:
            return False, "GitHub token not found in secrets. Backup disabled."

        if token == "your_github_token_here":
            return False, "Please configure your actual GitHub token in .streamlit/secrets.toml"
            
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

def delete_from_github(file_name):
    """
    Deletes a file from the GitHub repository.
    Requires 'GITHUB_TOKEN' in st.secrets.
    """
    try:
        token = get_github_token()
        if not token:
            return False, "GitHub token not found in secrets. Deletion disabled."

        if token == "your_github_token_here":
            return False, "Please configure your actual GitHub token in .streamlit/secrets.toml"
            
        g = Github(token)
        repo_name = "shawredanalytics/quxatstore" 
        repo = g.get_repo(repo_name)
        
        # Path in the repo
        repo_path = f"uploads/{file_name}"
        
        try:
            contents = repo.get_contents(repo_path)
            repo.delete_file(contents.path, f"Delete {file_name}", contents.sha)
            return True, f"File deleted from GitHub repository: {repo_name}"
        except GithubException as e:
            if e.status == 404:
                return True, "File not found in GitHub (already deleted?)"
            else:
                raise e
                
    except Exception as e:
        return False, f"GitHub deletion failed: {str(e)}"

@st.cache_resource
def sync_from_github():
    """
    Syncs files from GitHub repository 'uploads' folder to local 'uploads' directory.
    Run once per session start.
    """
    try:
        token = get_github_token()
        if not token:
            print("GitHub token not found in secrets. Sync disabled.")
            return

        if token == "your_github_token_here":
            print("Please configure your actual GitHub token in .streamlit/secrets.toml")
            return
            
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

def ensure_unique_codes():
    """
    Migrates metadata and drive links to ensure every resource has a unique QUXAT code.
    Syncs back to GitHub if changes are made.
    """
    changes_made = False
    
    # 1. Local Files Metadata
    metadata = load_metadata()
    meta_changed = False
    
    for filename in metadata:
        entry = metadata[filename]
        if isinstance(entry, str):
            # Convert old string format to dict
            metadata[filename] = {
                "type": entry,
                "code": generate_quxat_code()
            }
            meta_changed = True
        elif isinstance(entry, dict):
            if "code" not in entry:
                entry["code"] = generate_quxat_code()
                meta_changed = True
                
    if meta_changed:
        with open(METADATA_FILE, "w") as f:
            json.dump(metadata, f, indent=4)
        changes_made = True
        
    # 2. Drive Links
    drive_links = load_drive_links()
    links_changed = False
    
    for link in drive_links:
        if "code" not in link:
            link["code"] = generate_quxat_code()
            links_changed = True
            
    if links_changed:
        save_drive_links(drive_links)
        changes_made = True
        
    # 3. Sync back if needed
    if changes_made:
        try:
            print("Migrated data to include QUXAT codes. Syncing to GitHub...")
            if meta_changed:
                upload_to_github(METADATA_FILE, "metadata.json")
            if links_changed:
                upload_to_github(DRIVE_LINKS_FILE, "drive_links.json")
        except Exception as e:
            print(f"Error syncing migration to GitHub: {e}")

# Run sync on startup
sync_from_github()
ensure_unique_codes()

def get_files():
    metadata = load_metadata()
    files = []
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            if filename not in [".gitkeep", "metadata.json", "drive_links.json"]:
                file_path = os.path.join(UPLOAD_DIR, filename)
                stats = os.stat(file_path)
                
                # Handle both old (str) and new (dict) metadata
                meta_entry = metadata.get(filename, "General")
                if isinstance(meta_entry, dict):
                    doc_type = meta_entry.get("type", "General")
                    code = meta_entry.get("code", "N/A")
                else:
                    doc_type = meta_entry
                    code = "N/A"
                
                files.append(
                    {
                        "Filename": filename,
                        "Type": doc_type,
                        "Code": code,
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
        "QuXAT Healthcare Repository is a secure, centralized digital platform designed to help healthcare organizations efficiently access quality, safety and related compliance documents. "
        "The portal helps healthcare organizations to prepare for accreditation and regulatory requirements (such as JCI, NABH, NABL, ISO, and other healthcare standards), QuXAT ensures easy access to basic structured documentation with version control. "
        "Organizations can download resources and modify them as per their internal requirements."
    )
    st.link_button("Visit QuXAT Website", "https://www.quxat.com")
    
    st.markdown("---")
    
    # Stay Connected
    st.markdown("### Stay Connected")
    
    # Subscribe
    st.caption("Subscribe for updates regarding QuXAT Healthcare Repository")
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
    st.caption("Share QuXAT Healthcare Repository via Email")
    subject = "QuXAT Healthcare Repository"
    body = """Dear Team,

Greetings from QuXAT.

We are pleased to introduce the QuXAT Healthcare Repository, a secure and centralized digital platform designed to support healthcare organizations in efficiently accessing quality, safety, and compliance-related documentation.

The repository is developed to assist organizations in preparing for accreditation and regulatory requirements, including JCI, NABH, NABL, ISO, and other recognized healthcare standards. QuXAT provides basic, structured documentation with version control, ensuring clarity, consistency, and ease of use.

Key features of the QuXAT Healthcare Repository:
* Centralized access to quality and compliance documents
* Structured formats aligned with healthcare accreditation standards
* Version-controlled documents for better governance
* Downloadable resources that can be customized as per internal organizational requirements

Healthcare organizations can freely download the documents and modify them to suit their operational and compliance needs.

Free Access:
https://quxatstore.streamlit.app/

We hope the QuXAT Healthcare Repository will support your organization in strengthening quality systems and simplifying accreditation preparedness.

For any queries or support, please feel free to reach out.

Warm regards,
Team QuXAT"""
    subject_encoded = urllib.parse.quote(subject)
    body_encoded = urllib.parse.quote(body)
    mailto_link = f"mailto:?subject={subject_encoded}&body={body_encoded}"
    st.link_button("Share via Email 📧", mailto_link)
    
    st.markdown("---")
    
    # Support
    st.markdown("### QuXAT Repository Support")
    st.markdown("Need help? Connect with our support team!")
    
    whatsapp_url = "https://wa.me/916301237212"
    email_address = "quxat.team@gmail.com"
    
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <a href="{whatsapp_url}" target="_blank">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="40" alt="WhatsApp">
                </a>
                <a href="{whatsapp_url}" target="_blank" style="text-decoration: none; color: inherit; font-weight: bold;">
                    +91 6301237212
                </a>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <a href="mailto:{email_address}">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/7/7e/Gmail_icon_%282020%29.svg" width="40" alt="Email">
                </a>
                <a href="mailto:{email_address}" style="text-decoration: none; color: inherit; font-weight: bold;">
                    {email_address}
                </a>
            </div>
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
        st.image(logo_path, use_container_width=True)
st.title("QuXAT Healthcare Repository")
st.markdown("<h2 style='text-align: center; color: #2e7d32;'>✅ Free Access for all Healthcare Professionals</h2>", unsafe_allow_html=True)
st.subheader("Repository for Healthcare Quality & Compliance Documentation")
st.markdown("<p style='text-align: center;'>Access essential resources for JCI, NABH, NABL, ISO and other Healthcare Accreditation Standards.</p>", unsafe_allow_html=True)

# WhatsApp & Email Support Section (Below Hero)
st.markdown("### 📞 QuXAT Repository Support")
whatsapp_url = "https://wa.me/916301237212"
email_address = "quxat.team@gmail.com"

st.markdown(
    f"""
    <div style="display: flex; flex-direction: column; align-items: center; gap: 10px;">
        <div style="display: flex; justify-content: center; align-items: center; gap: 10px;">
            <a href="{whatsapp_url}" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="35" alt="WhatsApp">
            </a>
            <a href="{whatsapp_url}" target="_blank" style="text-decoration: none; color: inherit; font-size: 1.1em;">
                Connect with us on WhatsApp: <strong>+91 6301237212</strong>
            </a>
        </div>
        <div style="display: flex; justify-content: center; align-items: center; gap: 10px;">
            <a href="mailto:{email_address}">
                <img src="https://upload.wikimedia.org/wikipedia/commons/7/7e/Gmail_icon_%282020%29.svg" width="35" alt="Email">
            </a>
            <a href="mailto:{email_address}" style="text-decoration: none; color: inherit; font-size: 1.1em;">
                Email us: <strong>{email_address}</strong>
            </a>
        </div>
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
    
    local_files = get_files()
    drive_links = load_drive_links()
    
    # Process Drive Links
    drive_file_entries = []
    for link in drive_links:
        drive_file_entries.append({
            "Filename": link.get("name", "Unknown"),
            "Type": link.get("type", "General"),
            "Code": link.get("code", "N/A"),
            "Size (KB)": "Link",
            "Upload Date": link.get("added_on", "N/A"),
            "Source": "Google Drive",
            "URL": link.get("url", "#")
        })
        
    # Process Local Files
    local_file_entries = []
    for f in local_files:
        f["Source"] = "QuXAT Repository"
        f["URL"] = "" 
        local_file_entries.append(f)
        
    all_files = local_file_entries + drive_file_entries
    
    all_types = set()
    for f in all_files:
        doc_type = f.get("Type")
        if doc_type:
            all_types.add(doc_type)
    
    selected_types = []
    if all_types:
        selected_types = st.multiselect("Filter by Document Type", sorted(list(all_types)))
    
    if not all_files:
        st.info("No documents available yet.")
    else:
        df = pd.DataFrame(all_files)
        
        if selected_types:
            df = df[df["Type"].isin(selected_types)]
        
        if search_query:
            df = df[df["Filename"].str.contains(search_query, case=False)]
        
        if not df.empty:
            df_display = df.reset_index(drop=True)
            df_display["Sr. No"] = df_display.index + 1
            
            # Ensure session state for selection exists
            if "selected_filename" not in st.session_state:
                st.session_state.selected_filename = None

            # Apply selection state to the dataframe
            df_display["Select"] = df_display["Filename"] == st.session_state.selected_filename
            
            # Documents Section
            st.subheader("Available Documents")
            st.caption("Select a document from the table to preview or download.")

            # Configure columns for responsive table
            column_config = {
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    width="small",
                    default=False
                ),
                "Sr. No": st.column_config.NumberColumn(
                    "Sr. No",
                    width="small"
                ),
                "Filename": st.column_config.TextColumn(
                    "Filename",
                    width="large"
                ),
                "Type": st.column_config.TextColumn(
                    "Type",
                    width="small"
                ),
            }

            # Columns to display
            display_cols = ["Select", "Sr. No", "Filename", "Type", "Code"]
            
            # Interactive Dataframe
            edited_df = st.data_editor(
                df_display[display_cols],
                column_config=column_config,
                use_container_width=True,
                hide_index=True,
                disabled=["Sr. No", "Filename", "Type", "Code"],
                key="doc_selector"
            )
            
            # Handle Single Selection Logic
            selected_rows = edited_df[edited_df["Select"] == True]
            selected_filenames = set(selected_rows["Filename"].tolist())
            
            current_state_file = st.session_state.selected_filename
            
            # Check if current state file is visible in the current filtered view
            is_state_file_visible = current_state_file in df_display["Filename"].values

            # Detect changes
            newly_selected = [f for f in selected_filenames if f != current_state_file]
            
            if newly_selected:
                # User selected a new file -> Update state to this new file (enforce single selection)
                st.session_state.selected_filename = newly_selected[0]
                st.rerun()
            elif is_state_file_visible and current_state_file not in selected_filenames:
                # User deselected the currently selected file -> Clear state
                st.session_state.selected_filename = None
                st.rerun()

            # Display Action for Selected File
            if st.session_state.selected_filename:
                # Get the row from the original df (to ensure we have all data including URL/Source)
                # We use df (not df_display) to be safe, or just find it in df_display
                row_data = df[df["Filename"] == st.session_state.selected_filename]
                
                if not row_data.empty:
                    row = row_data.iloc[0]
                    
                    st.markdown("### Selected Document Action")
                    
                    col_info, col_btn = st.columns([3, 1])
                    
                    with col_info:
                        st.info(f"Selected: **{row['Filename']}** ({row['Source']})")
                    
                    with col_btn:
                        if row["Source"] == "Google Drive":
                             st.link_button("🔗 Open Link", row["URL"], use_container_width=True)
                        else:
                            # Use a unique key based on filename to avoid conflicts
                            if st.button("👁️ Preview / Download", key=f"btn_preview_{row['Filename']}", use_container_width=True):
                                file_path = os.path.join(UPLOAD_DIR, row["Filename"])
                                preview_document_modal(file_path, row["Filename"])

            st.markdown("<hr style='margin: 2px 0; border: 0; border-top: 2px solid #00796b;'>", unsafe_allow_html=True)
        else:
            st.info("No documents found matching your search.")

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
        # Sync Button (useful for multiple admins)
        if st.button("🔄 Sync Repository from GitHub"):
            with st.spinner("Syncing from GitHub..."):
                sync_from_github.clear()
                sync_from_github()
            st.success("Repository synced from GitHub!")
            st.rerun()

        tab1, tab2 = st.tabs(["Upload Local Document", "Manage Google Drive Links"])
        
        with tab1:
            st.subheader("Upload Local Document")

            uploaded_file = st.file_uploader("Choose a file", accept_multiple_files=False)
            doc_type = st.selectbox("Select Document Type", ["SOP", "Manual", "Forms", "Registers", "Work Instructions", "Posters", "QSP"])
            
            if uploaded_file is not None:
                # Check for duplicate file
                if os.path.exists(os.path.join(UPLOAD_DIR, uploaded_file.name)):
                    st.warning(f"⚠️ A file named '{uploaded_file.name}' already exists in the repository. Uploading will overwrite it.")

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
            st.subheader("Current QuXAT Repository Content")
            files = get_files()
            
            if files:
                df = pd.DataFrame(files)
                df_display = df.reset_index(drop=True)
                df_display.index = df_display.index + 1
                st.dataframe(df_display, use_container_width=True)
                
                st.markdown("### Delete Files")
                file_to_delete = st.selectbox("Select file to delete", [f["Filename"] for f in files])
                if st.button("Delete File"):
                    # 1. Delete local file
                    try:
                        os.remove(os.path.join(UPLOAD_DIR, file_to_delete))
                        st.success(f"File '{file_to_delete}' deleted locally!")
                    except Exception as e:
                        st.error(f"Error deleting local file: {e}")

                    # 2. Update metadata
                    metadata = load_metadata()
                    if file_to_delete in metadata:
                        del metadata[file_to_delete]
                        with open(METADATA_FILE, "w") as f:
                            json.dump(metadata, f, indent=4)
                    
                    # 3. Delete from GitHub
                    with st.spinner("Deleting from GitHub..."):
                        success, message = delete_from_github(file_to_delete)
                        if success:
                            st.success(message)
                            # 4. Sync metadata to GitHub
                            meta_success, meta_msg = upload_to_github(METADATA_FILE, "metadata.json")
                            if not meta_success:
                                 st.warning(f"Metadata update failed on GitHub: {meta_msg}")
                        else:
                            st.warning(message)

                    st.rerun()
            else:
                st.info("No documents uploaded yet.")

        with tab2:
            st.subheader("Manage Google Drive Links")
            drive_links = load_drive_links()
            
            # Form to Add/Edit
            with st.expander("Add / Edit Link", expanded=True):
                # Selection for edit mode
                link_options = ["New Link"] + [l["name"] for l in drive_links]
                selected_link_name = st.selectbox("Select Link to Edit (or New Link)", link_options)
                
                # Default values
                name_val = ""
                url_val = ""
                type_val = "SOP"
                
                if selected_link_name != "New Link":
                    # Find link data
                    link_data = next((l for l in drive_links if l["name"] == selected_link_name), None)
                    if link_data:
                        name_val = link_data.get("name", "")
                        url_val = link_data.get("url", "")
                        type_val = link_data.get("type", "SOP")
                
                with st.form("drive_link_form"):
                    new_name = st.text_input("Document Name", value=name_val)
                    new_url = st.text_input("Google Drive URL", value=url_val)
                    new_type = st.selectbox("Document Type", ["SOP", "Manual", "Forms", "Registers", "Work Instructions", "Posters", "QSP"], index=["SOP", "Manual", "Forms", "Registers", "Work Instructions", "Posters", "QSP"].index(type_val) if type_val in ["SOP", "Manual", "Forms", "Registers", "Work Instructions", "Posters", "QSP"] else 0)
                    
                    submitted = st.form_submit_button("Save Link")
                    
                    if submitted:
                        if new_name and new_url:
                            # Update or Add
                            # Remove old entry if editing (based on original name selected_link_name)
                            if selected_link_name != "New Link":
                                drive_links = [l for l in drive_links if l["name"] != selected_link_name]
                            
                            # Add new
                            drive_links.append({
                                "name": new_name,
                                "url": new_url,
                                "type": new_type,
                                "code": generate_quxat_code(),
                                "added_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            
                            saved_path = save_drive_links(drive_links)
                            st.success(f"Link '{new_name}' saved locally!")
                            
                            # Sync to GitHub
                            with st.spinner("Syncing to GitHub..."):
                                success, msg = upload_to_github(saved_path, "drive_links.json")
                                if success:
                                    st.success(msg)
                                else:
                                    st.error(msg)
                            st.rerun()
                        else:
                            st.warning("Please provide both Name and URL.")
            
            # Display and Delete
            if drive_links:
                st.subheader("Existing Links")
                df_links = pd.DataFrame(drive_links)
                st.dataframe(df_links, use_container_width=True)
                
                link_to_delete = st.selectbox("Select link to delete", [l["name"] for l in drive_links], key="del_link")
                if st.button("Delete Link"):
                    drive_links = [l for l in drive_links if l["name"] != link_to_delete]
                    saved_path = save_drive_links(drive_links)
                    st.success(f"Link '{link_to_delete}' deleted locally.")
                    
                    # Sync
                    with st.spinner("Syncing deletion to GitHub..."):
                        upload_to_github(saved_path, "drive_links.json")
                    
                    st.rerun()
            else:
                st.info("No Google Drive links added yet.")
    else:
        if password:
            st.error("Incorrect password")
