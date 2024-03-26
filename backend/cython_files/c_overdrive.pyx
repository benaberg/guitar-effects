import numpy as np
cimport numpy as np

DYTPE = np.float32
ctypedef np.float32_t DTYPE_t

cpdef np.ndarray[DTYPE_t, ndim=2] overdrive(np.ndarray[DTYPE_t, ndim=2] input_signal, double gain, double threshold):
    cdef np.ndarray[DTYPE_t, ndim=2] output_signal = np.zeros_like(input_signal)

    output_signal = np.tanh(input_signal * gain) * threshold

    return output_signal