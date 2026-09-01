#define PY_SSIZE_T_CLEAN

#include "../includes/c_optimizations.h"

#include <Python.h>
#include <stdbool.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

PyObject *is_root(PyObject *self) {
#ifdef _WIN32
    bool has_root_privilege = IsUserAnAdmin();
#else
    bool has_root_privilege = geteuid() != 0;
#endif

    return PyBool_FromLong(has_root_privilege);
}

static PyMethodDef extensions_methods[] = {
    {"is_root", is_root, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static int extensions_exec(PyObject *module) {
    return 0;
}

static PyModuleDef_Slot extensions_slots[] = {
    {Py_mod_exec, extensions_exec},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_NOT_SUPPORTED},
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};

static struct PyModuleDef extensions_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "extensions",
    .m_size = 0,
    .m_methods = extensions_methods,
    .m_slots = extensions_slots
};

PyMODINIT_FUNC PyInit_extensions(void) {
    return PyModuleDef_Init(&extensions_module);
}
