#include "simulatormodule.h"

char error_module[] = MODULE_NAME ".Error";
static struct module_state _state;

static PyObject *error_out(PyObject *m)
{
    struct module_state *st = GETSTATE(m);
    PyErr_SetString(st->error, "something bad happened");
    return NULL;
}

PyMODINIT_FUNC
MODULE_ENTRY_POINT(void)
{
    PyObject* simulator;

    simulator = Py_InitModule(MODULE_NAME, SimulatorMethods);

    if (simulator == NULL) INITERROR;
    struct module_state *st = GETSTATE(simulator);

    st->error = PyErr_NewException((char *) &error_module, NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(simulator);
        INITERROR;
    }
    // Register the BFM receive message callback
    // with the BFM manager
    cocotb_bfm_set_recv_msg_f(&bfm_recv_msg);


    add_module_constants(simulator);
}