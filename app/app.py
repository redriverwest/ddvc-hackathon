import streamlit as st
from datetime import datetime
import time

st.title('MidasAI')

markdown_filepath = "example.md"

if 'show_content' not in st.session_state:
    st.session_state.show_content = False

welcome = st.empty()
if not st.session_state.show_content:
    welcome.markdown("👋 Welcome! Would you like your assistant to create some actions tailored to your portfolio?")
    
    if st.button('Start MidasAI'):
        with st.spinner('Loading...'):
            messages = [
                "Please wait, we're preparing your portfolio actions!",
                "Fetching the best actions for you...",
                "Almost there, just a few seconds...",
                "Getting everything ready for you...",
                "All set! You're ready to go."
            ]
            
            message_container = st.empty()

            for message in messages:
                message_container.write(message)
                time.sleep(1)
            
            message_container.empty()
        
        st.session_state.show_content = True
        welcome.empty()

if st.session_state.show_content:
    if st.button('Refresh'):
        st.rerun()
        
    markdown_content = ""
    with open(markdown_filepath, 'r') as file:
        markdown_content = file.read()
    
    st.download_button(
        label="Download Markdown File",
        data=markdown_content,
        file_name="portfolio_actions.md",
        mime="text/markdown"
    )

    st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if 'checkboxes' not in st.session_state:
        st.session_state.checkboxes = {}

    def process_markdown(content):
        parts = content.split("## Potential Actions:")
        if len(parts) != 2:
            st.markdown(content)
            return
        
        st.markdown(parts[0])
        st.markdown("## Potential Actions:")
        
        actions = parts[1].split("###")[1:]
        for i, action in enumerate(actions):
            if action.strip():
                title = action.split('\n')[0].strip()
                checkbox_key = f"checkbox_{i}"
                
                if checkbox_key not in st.session_state.checkboxes:
                    st.session_state.checkboxes[checkbox_key] = False
                
                checked = st.checkbox(title, key=checkbox_key)
                content_lines = action.split('\n')[1:]
                if content_lines:
                    st.markdown('\n'.join(content_lines))
                st.markdown("---")

    process_markdown(markdown_content)
