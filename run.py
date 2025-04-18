import streamlit.cli as stcli
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", str(Path(__file__).parent / "pharma_dashboard" / "dashboard.py")]
    sys.exit(stcli.main()) 