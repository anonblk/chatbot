import streamlit as st
import pandas as pd
from openai import OpenAI

# Page config
st.set_page_config(page_title="📊 CSV Data Chat", layout="wide")

# Initialize OpenAI client with DeepSeek
client = OpenAI(
    api_key=st.secrets.get("DEEPSEEK_API_KEY", "optimalbet_eZUJHiYbKyVWzb95OQlQhnQjQumDbFVv"),
    base_url="https://api.deepseek.com"
)

# Title
st.title("📊 CSV Data Chat")
st.write("Upload a CSV file and ask questions about your data!")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

if uploaded_file:
    # Read CSV
    df = pd.read_csv(uploaded_file)

    # Store in session state
    if 'df' not in st.session_state:
        st.session_state.df = df

    # Display data
    st.subheader("📋 Your Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", len(df))
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")

    st.dataframe(df, use_container_width=True)

    # Chat section
    st.divider()
    st.subheader("💬 Ask Questions About Your Data")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about your CSV data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare data context for AI
        data_summary = f"""
You have access to a CSV dataset with the following information:

Columns: {', '.join(df.columns.tolist())}
Number of rows: {len(df)}

First few rows:
{df.head(10).to_string()}

Data types:
{df.dtypes.to_string()}

Basic statistics:
{df.describe().to_string()}

Answer the user's question based on this data.
"""

        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "You are a helpful data analyst assistant. Answer questions about the CSV data provided."},
                            {"role": "system", "content": data_summary},
                            *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                        ],
                        stream=False
                    )
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

else:
    st.info("👆 Upload a CSV file to get started!")

    # Example
    st.subheader("💡 Example")
    st.write("Once you upload a CSV, you can ask questions like:")
    st.markdown("""
    - What are the main trends in this data?
    - What's the average of column X?
    - Show me insights about the data
    - Which column has the highest values?
    - Summarize this data for me
    """)
