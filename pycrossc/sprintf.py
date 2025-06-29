from cffi import FFI

ffi = FFI()
lib = ffi.dlopen("msvcrt")
ffi.cdef("int sprintf(char *str, const char *format, ...);")

def sprintf(fmt, *args, bufsize=256):
	fmt = fmt.encode() if isinstance(fmt, str) else fmt
	c_args = []
	for arg in args:
		if isinstance(arg, str):
			c_args.append(ffi.new("char[]", arg.encode()))
		elif isinstance(arg, int):
			c_args.append(ffi.cast("int", arg))
		elif isinstance(arg, float):
			c_args.append(ffi.cast("double", arg))
		else:
			c_args.append(arg)

	buf = ffi.new(f"char[{bufsize}]")
	lib.sprintf(buf, fmt, *c_args)
	return ffi.string(buf)
