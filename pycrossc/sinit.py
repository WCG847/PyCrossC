from ctypes import CFUNCTYPE, c_void_p, POINTER, cast

FUNC_TYPE = CFUNCTYPE(None)

def __call_static_initializers(start: POINTER(c_void_p), end: POINTER(c_void_p)):
    size = end - start
    for i in range(size):
        func_ptr = cast(start[i], FUNC_TYPE)
        func_ptr()

def __initialize_cpp_rts(start: POINTER(c_void_p), end: POINTER(c_void_p)):
	__call_static_initializers(start, end)