export const GeneratorFunction = Object.getPrototypeOf(function* () { }).constructor;
export const ColorArray = Uint32Array;
export const RGBAArray = Uint8ClampedArray;
export function infer_type(a0, a1) {
    if (a0 instanceof Float64Array || a0 instanceof Array)
        return Float64Array;
    if (a1 instanceof Float64Array || a1 instanceof Array)
        return Float64Array;
    return Float32Array;
}
export const ScreenArray = Float32Array;
export function to_screen(array) {
    if (!(array instanceof Float32Array))
        return Float32Array.from(array);
    else
        return array;
}
export { BitSet as Indices } from "./util/bitset";
//# sourceMappingURL=types.js.map