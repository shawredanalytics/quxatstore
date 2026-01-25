import streamlit as st
import os
import shutil
import base64
from datetime import datetime
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer

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
    if logo_path:
        st.image(logo_path, use_container_width=True)
    else:
        st.image("https://via.placeholder.com/150x50?text=QuXAT", use_container_width=True) # Placeholder for logo
        
    page = st.selectbox("Navigation", ["Document Search", "Admin Upload"])
    st.markdown("---")
    st.markdown("### About QuXAT")
    st.info(
        "The QuXAT Score is a simple, credible indicator of compliance with essential quality and safety practices. "
        "It enables organizations to self-assess and benchmark on quality & safety maturity, identify gaps, and track progress over time."
    )
    st.link_button("Visit QuXAT Website", "https://www.quxat.com")
    st.markdown("© 2025 QuXAT - All Rights Reserved.")

# Title
st.title("QuXAT Store")
st.subheader("Organizational Quality & Safety Documentation Repository")
st.markdown("---")

if page == "Document Search":
    if logo_path:
        col1, col2 = st.columns([1, 6])
        with col1:
            st.image(logo_path, width=80)
        with col2:
            st.header("Search Documents")
    else:
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
                        pdf_viewer(input=pdf_data, width=700)
                    
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
        col1, col2 = st.columns([1, 6])
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
