import re
from typing import Optional

import pandas as pd
from pandas.api.types import is_object_dtype, is_string_dtype
import streamlit as st

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

def _safe_widget_key(prefix: str) -> str:
    """Generate a Streamlit-safe key from any string."""
    sanitized = re.sub(r"[^0-9a-zA-Z_-]+", "_", prefix)
    return sanitized or "widget"


def _filtered_file_name(name: str, *, suffix: str = "_filtered") -> str:
    """Return a descriptive download name preserving the original extension."""
    if not suffix:
        return name

    if "." in name:
        base, ext = name.rsplit(".", 1)
        return f"{base}{suffix}.{ext}"

    return f"{name}{suffix}.csv"


def _capitalize_team_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the dataframe with any team columns title-cased."""

    team_columns = [
        column for column in df.columns if re.search(r"team", column, re.IGNORECASE)
    ]

    if not team_columns:
        return df

    capitalized_df = df.copy()

    for column in team_columns:
        if is_string_dtype(capitalized_df[column]) or is_object_dtype(capitalized_df[column]):
            capitalized_df[column] = capitalized_df[column].apply(
                lambda value: value.title() if isinstance(value, str) else value
            )

    return capitalized_df


def show_dataset(
    name: str,
    df: pd.DataFrame,
    *,
    file_size: Optional[int] = None,
    key_prefix: Optional[str] = None,
    download_name: Optional[str] = None,
    add_filtered_suffix: bool = True,
) -> None:
    """Render metrics, filters and data preview for a CSV dataset."""

    key_prefix = key_prefix or name
    widget_key = _safe_widget_key(key_prefix)

    df = _capitalize_team_columns(df)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", len(df))
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        size_text = f"{file_size / 1024:.1f} KB" if file_size is not None else "—"
        st.metric("Size", size_text)

    if df.empty:
        st.warning("This file has no rows to display.")
        return

    view_options = st.expander("🔍 View options", expanded=False)
    with view_options:
        available_columns = list(df.columns)
        selected_columns = st.multiselect(
            "Columns to display",
            options=available_columns,
            default=available_columns,
            key=f"{widget_key}_columns",
        )

        max_slider_rows = int(min(len(df), 1000))
        default_rows = int(min(len(df), 100))
        max_rows = st.slider(
            "Rows to display",
            min_value=1,
            max_value=max_slider_rows,
            value=default_rows if default_rows >= 1 else 1,
            key=f"{widget_key}_rows",
        )

        keyword = st.text_input(
            "Filter rows by keyword",
            help="Searches all columns for the provided text (case insensitive).",
            key=f"{widget_key}_filter",
        ).strip()

    filtered_df = df
    if keyword:
        mask = filtered_df.astype(str).apply(
            lambda column: column.str.contains(keyword, case=False, na=False)
        )
        filtered_df = filtered_df[mask.any(axis=1)]

    if filtered_df.empty:
        st.info("No rows match the current filters.")
        return

    selected_df = filtered_df[selected_columns] if selected_columns else filtered_df

    if len(filtered_df) > max_rows:
        st.caption(
            f"Showing the first {max_rows} rows of {len(filtered_df)} matching rows. "
            "Download the CSV to access the full results."
        )
    st.dataframe(selected_df.head(max_rows), use_container_width=True)

    with st.expander("📋 Column information"):
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes.values,
            'Non-Null Count': df.count().values,
            'Null Count': df.isnull().sum().values
        })
        st.dataframe(col_info, use_container_width=True)

    numeric_columns = selected_df.select_dtypes(include='number')
    if not numeric_columns.empty:
        with st.expander("📈 Summary statistics"):
            st.dataframe(
                numeric_columns.describe().transpose(),
                use_container_width=True,
            )

    csv = selected_df.to_csv(index=False).encode('utf-8')
    base_download_name = download_name or name
    filtered_name = _filtered_file_name(
        base_download_name,
        suffix="_filtered" if add_filtered_suffix else "",
    )
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filtered_name,
        mime='text/csv',
        key=f"{widget_key}_download",
    )


if uploaded_files:
    # Create tabs if multiple files
    if len(uploaded_files) > 1:
        tabs = st.tabs([file.name for file in uploaded_files])

        for index, (tab, file) in enumerate(zip(tabs, uploaded_files)):
            with tab:
                try:
                    df = pd.read_csv(file)
                    show_dataset(
                        file.name,
                        df,
                        file_size=file.size,
                        key_prefix=f"uploaded_{index}_{file.name}",
                        download_name=file.name,
                    )
                except Exception as e:
                    st.error(f"Error reading {file.name}: {str(e)}")
    else:
        # Single file
        file = uploaded_files[0]
        try:
            df = pd.read_csv(file)
            show_dataset(
                file.name,
                df,
                file_size=file.size,
                key_prefix=f"uploaded_single_{file.name}",
                download_name=file.name,
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
    show_dataset(
        "sample_data.csv",
        sample_data,
        key_prefix="sample",
        download_name="sample_data.csv",
        add_filtered_suffix=False,
    )
