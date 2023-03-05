#!/usr/bin/env python

""" Build and install third party dependencies for PyMesh.
"""

import argparse
import subprocess
import os
import os.path
import tempfile
import shutil
import sys

class Dep:
    def __init__(self, name, required=False):
        self.name = name
        self.required = required

def get_third_party_dependencies():
    return [Dep("cgal"),
            Dep("cork"),
            Dep("eigen", required=True),
            Dep("tetgen"),
            Dep("triangle"),
            Dep("qhull"),
            Dep("clipper"),
            Dep("draco"),
            Dep("tbb"),
            Dep("mmg"),
            Dep("json", required=True)]

def parse_args():
    parser = argparse.ArgumentParser(__doc__);
    parser.add_argument("--cleanup", action="store_true",
            help="Clean up the build folder after done.");
    parser.add_argument("package",
            choices=["all"] + [dep.name for dep in get_third_party_dependencies()]);
    return parser.parse_args();

def get_pymesh_dir():
    return os.path.join(sys.path[0], "..");

def build_generic(libname, build_flags="", cleanup=True, optional=False):
    pymesh_dir = get_pymesh_dir();
    src_dir = os.path.join(pymesh_dir, "third_party", libname)
    cmakelists_path = os.path.join(src_dir, "CMakeLists.txt")
    if optional and not os.path.exists(os.path.join(src_dir, "CMakeLists.txt")):
        print("{} not found – skipping.".format(cmakelists_path))
        return

    build_dir = os.path.join(pymesh_dir, "third_party", "build", libname);
    if not os.path.exists(build_dir):
        os.makedirs(build_dir);

    # Configure cgal
    cmd = "cmake" + \
            " {}/third_party/{}".format(pymesh_dir, libname) + \
            " -DBUILD_SHARED_LIBS=Off" + \
            " -DCMAKE_POSITION_INDEPENDENT_CODE=On" + \
            build_flags + \
            " -DCMAKE_INSTALL_PREFIX={}/python/pymesh/third_party/".format(pymesh_dir);
    subprocess.check_call(cmd.split(), cwd=build_dir);

    # Build cgal
    cmd = "cmake --build {}".format(build_dir);
    subprocess.check_call(cmd.split());

    cmd = "cmake --build {} --target install".format(build_dir);
    subprocess.check_call(cmd.split());

    # Clean up
    if cleanup:
        shutil.rmtree(build_dir)

def build(package, cleanup, optional=False):
    if package == "all":
        for dep in get_third_party_dependencies():
            build(dep.name, cleanup, optional=(not dep.required));
    elif package == "cgal":
        build_generic("cgal",
                " -DWITH_CGAL_ImageIO=Off -DWITH_CGAL_Qt5=Off",
                cleanup=cleanup);
    elif package == "clipper":
        build_generic("Clipper/cpp", cleanup=cleanup, optional=optional);
    elif package == "tbb":
        build_generic("tbb",
                " -DTBB_BUILD_SHARED=On -DTBB_BUILD_STATIC=Off",
                cleanup=cleanup, optional=optional);
    elif package == "json":
        build_generic("json",
                " -DJSON_BuildTests=Off",
                cleanup=cleanup, optional=optional);
    else:
        build_generic(package, cleanup=cleanup, optional=optional);

def main():
    args = parse_args();
    build(args.package, args.cleanup);

if __name__ == "__main__":
    main();
