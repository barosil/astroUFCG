from pathlib import Path

code_folder = Path("../../src/")
data_folder = code_folder / "../data"
notebooks_folder = code_folder / "../notebooks"
temp_folder = code_folder / "../temp"
if not temp_folder.exists():
    data_folder.mkdir(parents=True)
main_folder = code_folder / "../content/02_main"
