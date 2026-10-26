"""
Build script to compile the native C core (nody_core.c) into nody/nody_core.dll.
Uses Microsoft Visual C++ (MSVC) cl.exe with /O2 speed optimizations.
"""

import subprocess
import os
import sys

VCVARS_PATHS = [
    r"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat",
    r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars32.bat",
    r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars32.bat",
]


def build():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    c_src = os.path.join(root_dir, "c_src", "nody_core.c")
    output_dll = os.path.join(root_dir, "nody", "nody_core.dll")
    include_dir = os.path.join(root_dir, "c_src")

    vcvars_bat = None
    for p in VCVARS_PATHS:
        if os.path.exists(p):
            vcvars_bat = p
            break

    if not vcvars_bat:
        print("Error: Could not locate vcvars32.bat for MSVC.", file=sys.stderr)
        sys.exit(1)

    cmd = (
        f'cmd /c ""{vcvars_bat}" && '
        f'cl /O2 /LD /I "{include_dir}" "{c_src}" /Fe:"{output_dll}""'
    )

    print(f"Compiling {c_src} -> {output_dll} with /O2 optimizations...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # Clean intermediate build files (.obj, .lib, .exp)
    for ext in [".obj", ".exp", ".lib"]:
        for f in [f"nody_core{ext}", os.path.join("nody", f"nody_core{ext}")]:
            p = os.path.join(root_dir, f)
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass

    if result.returncode == 0:
        print("[SUCCESS] Successfully compiled nody_core.dll!")
    else:
        print("[FAILED] Compilation error:", file=sys.stderr)
        print(result.stderr or result.stdout, file=sys.stderr)
        sys.exit(result.returncode)


if __name__ == "__main__":
    build()
