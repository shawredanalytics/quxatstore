import streamlit as st
import os
import shutil
from datetime import datetime
import pandas as pd

# Page config
st.set_page_config(
    page_title="QuXAT Store",
    page_icon="📚",
    layout="wide"
)

# Constants
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Helper functions
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
page = st.sidebar.selectbox("Navigation", ["Document Search", "Admin Upload"])

# Title
st.title("📚 QuXAT Store")
st.markdown("Quality Systems Documentation Repository")

if page == "Document Search":
    st.header("Search Documents")
    
    # Search bar
    search_query = st.text_input("Search documents by name...")
    
    # Get files
    files = get_files()
    
    if files:
        df = pd.DataFrame(files)
        
        # Filter if search query exists
        if search_query:
            df = df[df['Filename'].str.contains(search_query, case=False)]
        
        if not df.empty:
            # Display files
            st.dataframe(df, use_container_width=True)
            
            # Download section
            st.subheader("Download Files")
            selected_file = st.selectbox("Select a file to download", df['Filename'])
            
            if selected_file:
                file_path = os.path.join(UPLOAD_DIR, selected_file)
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"Download {selected_file}",
                        data=f,
                        file_name=selected_file,
                        mime="application/octet-stream"
                    )
        else:
            st.info("No documents found matching your search.")
    else:
        st.info("No documents uploaded yet.")

elif page == "Admin Upload":
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
        st.subheader("Manage Files")
        files = get_files()
        if files:
            file_to_delete = st.selectbox("Select file to delete", [f['Filename'] for f in files])
            if st.button("Delete File"):
                os.remove(os.path.join(UPLOAD_DIR, file_to_delete))
                st.success(f"File '{file_to_delete}' deleted!")
                st.rerun()
    else:
        if password:
            st.error("Incorrect password")
