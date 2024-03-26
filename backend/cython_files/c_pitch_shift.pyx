import numpy as np
import librosa as lib
cimport numpy as np
cimport librosa as lib

DYTPE = np.float32
ctypedef np.float32_t DTYPE_t

cpdef np.ndarray[DTYPE_t, ndim=1] pitch_shift(np.ndarray[DTYPE_t, ndim=1] input_signal, double shift, int rate):
        cdef int target_sampling_rate = int(rate * shift)
        cdef np.ndarray[DTYPE_t, ndim=1] stretched_signal = time_stretch(input_signal, shift)
        cdef np.ndarray[DTYPE_t, ndim=1] resampled_signal = lib.resample(stretched_signal, orig_sr=rate, target_sr=target_sampling_rate * 2) 

        ### START FILTER

        # Create two signals phase-shifted by 180 degrees
        cdef np.ndarray[DTYPE_t, ndim=1] signal1 = resampled_signal[::2]
        cdef np.ndarray[DTYPE_t, ndim=1] signal2 = resampled_signal[1::2]
        
        # Modulate amplitude using triangular distribution
        cdef np.ndarray[DTYPE_t, ndim=1] fade_in = np.linspace(0, 1, len(signal1) // 2, dtype=DYTPE)
        cdef np.ndarray[DTYPE_t, ndim=1] fade_out = np.linspace(1, 0, len(signal1) // 2, dtype=DYTPE)
        cdef np.ndarray[DTYPE_t, ndim=1] fade = np.concatenate((fade_in, fade_out))
        
        signal1 *= fade
        signal2 *= fade[::-1]  # Reverse fade for second signal

        cdef np.ndarray[DTYPE_t, ndim=1] output_signal = signal1 + signal2

        return output_signal

        ### END FILTER

cpdef np.ndarray[DTYPE_t, ndim=1] time_stretch(np.ndarray[DTYPE_t, ndim=1] input_signal, double stretch_factor):
    cdef np.ndarray[DTYPE_t, ndim=1] output_signal = lib.effects.time_stretch(input_signal, rate=stretch_factor)
    
    return output_signal