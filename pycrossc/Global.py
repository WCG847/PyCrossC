def __register_global_object(obj: any, destructor, node: list = None):
	global __global_destructor_chain
	node = [__global_destructor_chain, destructor, obj]
	__global_destructor_chain = node