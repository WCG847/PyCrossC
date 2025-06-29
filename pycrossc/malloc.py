from ctypes import *
from typing import BinaryIO
from typing_extensions import Self
from io import BufferedIOBase, IOBase, UnsupportedOperation

malloc = cdll.msvcrt.malloc
malloc.argtypes = [c_size_t]
malloc.restype = c_void_p
free = cdll.msvcrt.free
free.argtypes = [c_void_p]
free.restype = None
memset = cdll.msvcrt.memset
memset.argtypes = [c_void_p, c_int, c_size_t]
memset.restype = c_void_p
realloc = cdll.msvcrt.realloc
realloc.argtypes = [c_void_p, c_size_t]
realloc.restype = c_void_p
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2


class MallocIO(BufferedIOBase, IOBase):
	def __init__(self, initial_bytes: c_size_t = 64) -> None:
		self.buffer = self.malloc(initial_bytes)
		self.ptr = self.buffer
		self.size = initial_bytes
		self.offset = 0
		self.leftover = 0

	def __del__(self):
		try:
			if self.buffer is not None:
				self.close()
		except AttributeError:
			pass

	def __repr__(self):
		return f"<MallocIO size={self.size} offset={self.offset} ptr={hex(self.grabptr())}>"

	def _check_closed(self):
		if self.buffer is None:
			raise ValueError("I/O operation on closed buffer.")

	def __enter__(self) -> Self:
		return self

	def __exit__(self, exc_type, exc_value, traceback) -> None:
		self.close()

	def resize(self, size: c_size_t = None) -> c_void_p:
		self._check_closed()
		new_size = size or self.leftover
		new_buf = realloc(self.buffer, new_size)
		if not new_buf:
			raise MemoryError("realloc failed")
		self.buffer = new_buf
		self.ptr = self.buffer
		self.size = new_size
		if self.offset > new_size:
			self.offset = new_size
		return self.buffer

	def grabptr(self) -> int:
		return cast(self.ptr, c_void_p).value

	def set(self, content, size):
		self._check_closed()
		return memset(self.buffer, content, size)

	@staticmethod
	def malloc(size: c_size_t) -> c_void_p:
		return malloc(size)

	def close(self) -> None:
		free(self.buffer)
		self.buffer = None

	def seek(self, offset: int, whence=SEEK_SET):
		self._check_closed()
		if whence == SEEK_SET:
			new_pos = offset
		elif whence == SEEK_CUR:
			new_pos = self.offset + offset
		elif whence == SEEK_END:
			new_pos = self.size + offset
		else:
			raise ValueError("Invalid whence")
		if not (0 <= new_pos <= self.size):
			raise BufferError("Seek out of bounds")
		self.offset = new_pos
		return self.offset

	def tell(self):
		self._check_closed()
		return self.offset

	def read(self, n: int = 1) -> bytes:
		self._check_closed()
		if self.offset + n > self.size:
			raise BufferError("Read beyond buffer")
		result = string_at(self.ptr + self.offset, n)
		self.offset += n
		return result

	def readinto(self, b: bytearray) -> int:
		self._check_closed()
		n = len(b)
		if self.offset + n > self.size:
			n = self.size - self.offset
		memmove((c_char * n).from_buffer(b), self.ptr + self.offset, n)
		self.offset += n
		return n

	def readable(self) -> bool:
		return True

	def writable(self) -> bool:
		return True

	def seekable(self) -> bool:
		return True

	def peek(self, n: int = 1) -> bytes:
		self._check_closed()
		if self.offset + n > self.size:
			n = self.size - self.offset
		return string_at(self.ptr + self.offset, n)

	def getvalue(self) -> bytes:
		self._check_closed()
		return string_at(self.ptr, self.size)

	def truncate(self, size: int = None):
		self._check_closed()
		size = size if size is not None else self.offset
		if size > self.size:
			self.resize(size)
		self.size = size
		if self.offset > size:
			self.offset = size
		return size

	def write(self, data: bytes) -> int:
		self._check_closed()
		if self.offset + len(data) > self.size:
			self.leftover = self.offset + len(data)
			self.resize()
		memmove(self.ptr + self.offset, data, len(data))
		self.offset += len(data)
		return len(data)

	def flush(self):
		raise UnsupportedOperation("Malloc doesn't flush. It leaks.")

	def detach(self):
		raise UnsupportedOperation("You can't detach from raw malloc.")