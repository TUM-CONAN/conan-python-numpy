import os

from conan import ConanFile
from conan.tools.files import copy, get, chdir
from conan.tools.layout import basic_layout
from conan.tools.env import Environment

required_conan_version = ">=1.52.0"

class PythonNumpyConan(ConanFile):
    python_requires = "camp_common/0.5@camposs/stable"
    python_requires_extend = "camp_common.CampPythonBase"

    name = "python-numpy"
    version = "2.2.0"
    license = "MIT"
    description = "Numpy extension for Python Interpreter"

    settings = "os", "compiler", "build_type", "arch"


    options = { 
        "python": ["ANY"],
        "python_version": [None, "3.12", ],
        "with_system_python": [True, False],
    }

    default_options = {
        "python": "python3",
        "python_version": "3.12",
        "with_system_python": False,
    }

    @property
    def pyver(self):
        pyver = self.options.python_version
        if self.options.with_system_python:
            pyver = ".".join(self._python_version.split(".")[1:2])
        return pyver

    @property
    def python_lib_path(self):
        return os.path.join(self.package_folder, "lib", f"python{self.pyver}", "site-packages")
    
    @property
    def active_python_exec(self):
        if not self.options.with_system_python:
            cpython = self.dependencies["cpython"]
            return os.path.join(cpython.package_folder, "bin", "python")
        return self._python_exec

    def build_requirements(self):
        if not self.options.with_system_python:
            self.requires("cpython/[~{}]".format(self.options.python_version))
            self.build_requires("python-pip/24.3.1@camposs/stable")
            self.build_requires("python-setuptools/75.6.0@camposs/stable")
            self.build_requires("cython/3.0.11-1@camposs/stable")

    def requirements(self):
        self.requires("clapack/3.2.1@camposs/stable")

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        env1 = Environment()
        env1.define("PYTHONPATH", self.python_lib_path)
        envvars = env1.vars(self)
        envvars.save_script("py_env_file")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        if not os.path.isdir(self.python_lib_path):
            os.makedirs(self.python_lib_path)
        with chdir(self, self.source_folder):
            self.run('{0} -m pip install --prefix= --root="{1}" .'.format(self.active_python_exec, self.package_folder))

    def package(self):
        os.makedirs(os.path.join(self.package_folder, "include"))
        copy(self, 
            "*.h", 
            os.path.join(self.source_folder, "src", "numpy", "_core", "include", "numpy"),
            os.path.join(self.package_folder, "include", "numpy"),
            keep_path=True
            )

    def package_info(self):
        self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "lib", f"python{self.pyver}", "site-packages"))
        self.buildenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "lib", f"python{self.pyver}", "site-packages"))

