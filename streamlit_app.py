import os
import runpy

# Execute the existing frontend Streamlit script so Streamlit Cloud
# can run the app by using this repository's root entrypoint.
runpy.run_path(os.path.join(os.path.dirname(__file__), "frontend", "ui.py"), run_name="__main__")
