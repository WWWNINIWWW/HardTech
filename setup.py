from cx_Freeze import setup, Executable


# build_exe_options = {"packages": [""], "includes": ["serial", 'psutil', 'requests']}

build_exe_options = {"includes": ["serial", 'psutil', 'requests']}

executables = [Executable("espFORServer.py", base="Win32GUI", target_name="HardTech Driver", uac_admin=True, shortcut_name="HardTech")]


setup(
    name="HardTech Driver",
    version="1.1",
    description="Driver Suporte de Notebook by HardTech",
    options={"build_exe": build_exe_options},
    executables=executables
)

# python setup.py build