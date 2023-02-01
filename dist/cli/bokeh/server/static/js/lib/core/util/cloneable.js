import { entries } from "./object";
import { isPlainObject, isObject, isArray, isBoolean, isNumber, isString } from "./types";
//| Map<CloneableType, CloneableType>
//| Set<CloneableType>
export const clone = Symbol("clone");
export function is_Cloneable(obj) {
    return isObject(obj) && obj[clone] !== undefined;
}
export class CloningError extends Error {
}
CloningError.__name__ = "CloningError";
export class Cloner {
    constructor() { }
    clone(obj) {
        if (is_Cloneable(obj))
            return obj[clone](this);
        else if (isArray(obj)) {
            const n = obj.length;
            const result = new Array(n);
            for (let i = 0; i < n; i++) {
                const value = obj[i];
                result[i] = this.clone(value);
            }
            return result;
        }
        else if (isPlainObject(obj)) {
            const result = {};
            for (const [key, value] of entries(obj)) {
                result[key] = this.clone(value);
            }
            return result;
        }
        else if (obj === null || isBoolean(obj) || isNumber(obj) || isString(obj)) {
            return obj;
        }
        else
            throw new CloningError(`${Object.prototype.toString.call(obj)} is not cloneable`);
    }
}
Cloner.__name__ = "Cloner";
//# sourceMappingURL=cloneable.js.map