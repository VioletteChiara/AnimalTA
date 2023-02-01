import { assert } from "./util/assert";
import { entries } from "./util/object";
import { isPlainObject, isObject, isArray, isTypedArray, isBoolean, isNumber, isString } from "./util/types";
//| Map<SerializableType, SerializableType>
//| Set<SerializableType>
//| ArrayBuffer
// TypedArray?
export const serialize = Symbol("serialize");
function is_Serializable(obj) {
    return isObject(obj) && obj[serialize] !== undefined;
}
export class SerializationError extends Error {
}
SerializationError.__name__ = "SerializationError";
export class Serializer {
    constructor(options) {
        this._references = new Map();
        this._definitions = new Map();
        this._refmap = new Map();
        this.include_defaults = options?.include_defaults ?? true;
    }
    get_ref(obj) {
        return this._references.get(obj);
    }
    add_ref(obj, ref) {
        assert(!this._references.has(obj));
        this._references.set(obj, ref);
    }
    add_def(obj, def) {
        const ref = this.get_ref(obj);
        assert(ref != null);
        this._definitions.set(obj, def);
        this._refmap.set(ref, def);
    }
    get objects() {
        return new Set(this._references.keys());
    }
    get references() {
        return new Set(this._references.values());
    }
    get definitions() {
        return new Set(this._definitions.values());
    }
    resolve_ref(ref) {
        return this._refmap.get(ref);
    }
    remove_ref(obj) {
        return this._references.delete(obj);
    }
    remove_def(obj) {
        return this._definitions.delete(obj);
    }
    to_serializable(obj) {
        const ref = this.get_ref(obj);
        if (ref != null)
            return ref;
        else if (is_Serializable(obj))
            return obj[serialize](this);
        else if (isArray(obj) || isTypedArray(obj)) {
            const n = obj.length;
            const result = new Array(n);
            for (let i = 0; i < n; i++) {
                const value = obj[i];
                result[i] = this.to_serializable(value);
            }
            return result;
        }
        else if (isPlainObject(obj)) {
            const result = {};
            for (const [key, value] of entries(obj)) {
                result[key] = this.to_serializable(value);
            }
            return result;
        }
        else if (obj === null || isBoolean(obj) || isNumber(obj) || isString(obj)) {
            return obj;
        }
        else
            throw new SerializationError(`${Object.prototype.toString.call(obj)} is not serializable`);
    }
}
Serializer.__name__ = "Serializer";
//# sourceMappingURL=serializer.js.map