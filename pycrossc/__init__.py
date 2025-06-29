from .Global import __register_global_object, __global_destructor_chain
from .malloc import *
from .sinit import __call_static_initializers, __initialize_cpp_rts
from .printf import printf
from .sprintf import sprintf