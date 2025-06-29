from cffi import FFI

ffi = FFI()
lib = ffi.dlopen("msvcrt")
ffi.cdef("int printf(const char *fmt, ...);")

def printf(fmt, *args):
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
	return lib.printf(fmt, *c_args)

if __name__ == '__main__':
	printf("%d %s %f\n", 123, "test", 9.81)
