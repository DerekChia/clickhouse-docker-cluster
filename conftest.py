import sys, pathlib

this_file_path = pathlib.Path(__file__)
src_core_dir_path_str = str(this_file_path.parent.joinpath('src', 'core'))

# commenting out this line causes "Module not found" on "import bubble" in __main__.py
sys.path.insert(0, src_core_dir_path_str)