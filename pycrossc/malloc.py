from ctypes import *
from typing import BinaryIO
from typing_extensions import Self
from io import UnsupportedOperation

malloc = cdll.msvcrt.malloc
malloc.argtypes = [c_size_t]
malloc.restype = c_void_p
free = cdll.msvcrt.free
free.argtypes = [c_void_p]
free.restype = None
memset = cdll.msvcrt.memset
memset.argtypes = [c_void_p, c_int, c_size_t]
memset.restype = c_void_p
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2


class MallocIO(BinaryIO):
    def __init__(self, initial_bytes: c_size_t = 64) -> None:
        self.buffer = self.malloc(initial_bytes)
        self.ptr = self.buffer
        self.size = initial_bytes
        self.offset = 0

    def __del__(self):
        try:
            if self.buffer:
                self.close()
        except AttributeError:
            pass

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def grabptr(self) -> int:
        return cast(self.ptr, c_void_p).value

    def set(self, content, size):
        return memset(self.buffer, content, size)

    @staticmethod
    def malloc(size: c_size_t) -> c_void_p:
        return malloc(size)

    def close(self) -> None:
        free(self.buffer)
        self.buffer = None

    def seek(self, offset: int, whence=SEEK_SET):
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
        return self.offset

    def read(self, n: int = 1) -> bytes:
        if self.offset + n > self.size:
            raise BufferError("Read beyond buffer")
        result = string_at(self.ptr + self.offset, n)
        self.offset += n
        return result

    def write(self, data: bytes) -> int:
        if self.offset + len(data) > self.size:
            raise BufferError("Write beyond buffer")
        memmove(self.ptr + self.offset, data, len(data))
        self.offset += len(data)
        return len(data)

    def flush(self):
        raise UnsupportedOperation("Malloc doesn't flush. It leaks.")

    def detach(self):
        raise UnsupportedOperation("You can't detach from raw malloc.")


# test
# if __name__ == "__main__":
#     mem = MallocIO(128)
#     byte = mem.read(128)
#     print(f" at {hex(mem.grabptr())}, {byte}. In int {hex(int.from_bytes(byte))}")
#     mem.close()