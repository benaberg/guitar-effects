import numpy as np
cimport numpy as np

DYTPE = np.float32
ctypedef np.float32_t DTYPE_t

cpdef np.ndarray[DTYPE_t, ndim=2] echo(np.ndarray[DTYPE_t, ndim=2] input_signal, double delay, double decay, int rate, np.ndarray[DTYPE_t, ndim=2] c_buffer, int buffer_index, int c_buffer_max, int iter):
    cdef int delay_samples = int(delay * rate)
    cdef int num_samples = input_signal.shape[0]
    cdef int i, delayed_index
    cdef np.ndarray[DTYPE_t, ndim=2] output_signal

    output_signal = np.zeros_like(input_signal)

    while i < num_samples:
        delayed_index = (buffer_index - delay_samples) % c_buffer_max
        output_signal[i] = input_signal[i] + c_buffer[delayed_index]
        c_buffer[buffer_index] = input_signal[i] + decay * c_buffer[buffer_index]
        buffer_index = (buffer_index + 1) % c_buffer_max
        i += 1

    return output_signal