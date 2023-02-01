import { isPlainObject } from "./types";
import { BYTE_ORDER } from "./platform";
import { swap, base64_to_buffer, buffer_to_base64 } from "./buffer";
export function is_NDArray_ref(v) {
    return isPlainObject(v) && ("__buffer__" in v || "__ndarray__" in v);
}
export function decode_NDArray(ref, buffers) {
    const { shape, dtype, order } = ref;
    let bytes;
    if ("__buffer__" in ref) {
        const buffer = buffers.get(ref.__buffer__);
        if (buffer != null)
            bytes = buffer;
        else
            throw new Error(`buffer for ${ref.__buffer__} not found`);
    }
    else {
        bytes = base64_to_buffer(ref.__ndarray__);
    }
    if (order !== BYTE_ORDER) {
        swap(bytes, dtype);
    }
    return { buffer: bytes, dtype, shape };
}
export function encode_NDArray(array, buffers) {
    const data = {
        order: BYTE_ORDER,
        dtype: array.dtype,
        shape: array.shape,
    };
    if (buffers != null) {
        const __buffer__ = `${buffers.size}`;
        buffers.set(__buffer__, array.buffer);
        return { __buffer__, ...data };
    }
    else {
        const __ndarray__ = {
            toJSON() {
                return buffer_to_base64(array.buffer);
            },
        };
        return { __ndarray__, ...data };
    }
}
//# sourceMappingURL=serialization.js.map