import { concat, union } from "./array";
const { hasOwnProperty } = Object.prototype;
export const { keys, values, entries, assign: extend } = Object;
export function clone(obj) {
    return { ...obj };
}
export function merge(obj1, obj2) {
    /*
     * Returns an object with the array values for obj1 and obj2 unioned by key.
     */
    const result = Object.create(Object.prototype);
    const keys = concat([Object.keys(obj1), Object.keys(obj2)]);
    for (const key of keys) {
        const arr1 = hasOwnProperty.call(obj1, key) ? obj1[key] : [];
        const arr2 = hasOwnProperty.call(obj2, key) ? obj2[key] : [];
        result[key] = union(arr1, arr2);
    }
    return result;
}
export function size(obj) {
    return Object.keys(obj).length;
}
export function is_empty(obj) {
    return size(obj) == 0;
}
/** @deprecated */
export const isEmpty = is_empty;
export function to_object(map) {
    const obj = {};
    for (const [key, val] of map) {
        obj[key] = val;
    }
    return obj;
}
//# sourceMappingURL=object.js.map