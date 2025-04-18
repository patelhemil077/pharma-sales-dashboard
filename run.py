import streamlit as st
import sys
from pathlib import Path

if __name__ == "__main__":
    dashboard_path = str(Path(__file__).parent / "pharma_dashboard" / "dashboard.py")
    sys.argv = ["streamlit", "run", dashboard_path]
    st.cli.main() 