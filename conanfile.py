import os

from conan import ConanFile
from conan.tools.files import copy, get, chdir
from conan.tools.layout import basic_layout
from conan.tools.env import Environment

required_conan_version = ">=1.52.0"

class PythonNumpyConan(ConanFile):
    python_requires = "camp_common/0.5@camposs/stable"
    python_requires_extend = "camp_common.CampPythonBase"

    package_type = "application"

    name = "python-numpy"
    version = "1.26.4"
    license = "MIT"
    description = "Numpy extension for Python Interpreter"

    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        if self._use_custom_python:
            self.requires("cpython/[~{}]@camposs/stable".format(self._python_version))
            self.build_requires("python-pip/24.3.1@camposs/stable")
            self.build_requires("python-setuptools/75.6.0@camposs/stable")
            self.build_requires("cython/3.0.11-1@camposs/stable")

    def requirements(self):
        self.requires("clapack/3.2.1@camposs/stable")

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        env1 = Environment()
        env1.define("PYTHONPATH", os.path.join(self.package_folder, "lib", f"python{self._python_version}", "site-packages"))
        envvars = env1.vars(self)
        envvars.save_script("py_env_file")

    def package_id(self):
        self.info.clear()
        if self.conf.get("user.camp.common:use_custom_python", default=None, check_type=str):
            self.info.conf.define("user.camp.common:use_custom_python", self.conf.get("user.camp.common:use_custom_python"))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        with chdir(self, self.source_folder):
            self.run('{0} -m pip install --prefix= --root="{1}" .'.format(self._python_exec, self.package_folder))

    def package(self):
        if self.version.split('.')[0] == '2':
            copy(self, 
                "*.h", 
                os.path.join(self.source_folder, "numpy", "_core", "include", "numpy"),
                os.path.join(self.package_folder, "include", "numpy"),
                keep_path=True
                )
            for name in ["_numpyconfig.h", "__multiarray_api.c", "__multiarray_api.h", "__ufunc_api.c", "__ufunc_api.h"]:
                copy(self,
                    name,
                    os.path.join(self.package_folder, "lib", f"python{self._python_version}", "site-packages", "numpy", "_core", "include", "numpy"),
                    os.path.join(self.package_folder, "include", "numpy"),
                    )
        else:
            copy(self, 
                "*.h", 
                os.path.join(self.source_folder, "numpy", "core", "include", "numpy"),
                os.path.join(self.package_folder, "include", "numpy"),
                keep_path=True
                )
            for name in ["_numpyconfig.h", "__multiarray_api.c", "__multiarray_api.h", "__ufunc_api.c", "__ufunc_api.h"]:
                copy(self,
                    name,
                    os.path.join(self.package_folder, "lib", f"python{self._python_version}", "site-packages", "numpy", "core", "include", "numpy"),
                    os.path.join(self.package_folder, "include", "numpy"),
                    )

    def package_info(self):
        self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "lib", f"python{self._python_version}", "site-packages"))
        self.buildenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "lib", f"python{self._python_version}", "site-packages"))

