import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="📊 CSV Table Viewer", layout="wide")

# Title
st.title("📊 CSV Table Viewer")
st.write("Upload CSV files to view them as tables")

# File uploader
uploaded_files = st.file_uploader(
    "Choose CSV file(s)",
    type=['csv'],
    accept_multiple_files=True
)

if uploaded_files:
    # Create tabs if multiple files
    if len(uploaded_files) > 1:
        tabs = st.tabs([file.name for file in uploaded_files])

        for tab, file in zip(tabs, uploaded_files):
            with tab:
                try:
                    df = pd.read_csv(file)

                    # Display stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Rows", len(df))
                    with col2:
                        st.metric("Columns", len(df.columns))
                    with col3:
                        st.metric("Size", f"{file.size / 1024:.1f} KB")

                    # Display dataframe
                    st.dataframe(df, use_container_width=True)

                    # Download button
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=file.name,
                        mime='text/csv',
                    )

                except Exception as e:
                    st.error(f"Error reading {file.name}: {str(e)}")
    else:
        # Single file
        file = uploaded_files[0]
        try:
            df = pd.read_csv(file)

            # Display stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Size", f"{file.size / 1024:.1f} KB")

            # Display dataframe
            st.dataframe(df, use_container_width=True)

            # Show column info
            with st.expander("📋 Column Information"):
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.values,
                    'Non-Null Count': df.count().values,
                    'Null Count': df.isnull().sum().values
                })
                st.dataframe(col_info, use_container_width=True)

            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=file.name,
                mime='text/csv',
            )

        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
else:
    st.info("👆 Upload one or more CSV files to get started")

    # Sample data demo
    st.subheader("📝 Example")
    sample_data = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Age': [25, 30, 35, 28],
        'City': ['New York', 'San Francisco', 'Los Angeles', 'Chicago'],
        'Score': [95, 87, 92, 88]
    })
    st.dataframe(sample_data, use_container_width=True)
