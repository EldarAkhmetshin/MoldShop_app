from cx_Freeze import setup, Executable

executables = [Executable('main.py')]

excludes = []

zip_include_packages = ['src','python-dotenv', 'Pillow', 'loguru', 'pandas', 'openpyxl', 'tkinter']


options = {
    'build_exe': {
        'include_msvcr': True,
        'excludes': excludes,
        'zip_include_packages': zip_include_packages,
        'build_exe': 'build_windows',
    }
}

setup(name='hello_world',
      version='0.0.12',
      description='My Hello World App!',
      executables=executables,
      options=options)