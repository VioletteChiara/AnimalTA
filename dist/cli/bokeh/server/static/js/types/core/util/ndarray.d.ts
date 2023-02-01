import { DataType } from "../types";
import { equals, Equatable, Comparator } from "./eq";
import { serialize, Serializable, Serializer } from "../serializer";
declare const __ndarray__: unique symbol;
export interface NDArrayType extends Equatable, Serializable {
    readonly [__ndarray__]: boolean;
    readonly dtype: DataType;
    readonly shape: number[];
    readonly dimension: number;
}
declare type Array1d = {
    dimension: 1;
    shape: [number];
};
declare type Array2d = {
    dimension: 2;
    shape: [number, number];
};
export declare type Uint32Array1d = Uint32NDArray & Array1d;
export declare type Uint8Array1d = Uint8NDArray & Array1d;
export declare type Uint8Array2d = Uint8NDArray & Array2d;
export declare type Float32Array2d = Float32NDArray & Array2d;
export declare type Float64Array2d = Float64NDArray & Array2d;
export declare type FloatArray2d = Float32Array2d | Float64Array2d;
export declare class Uint8NDArray extends Uint8Array implements NDArrayType {
    readonly [__ndarray__] = true;
    readonly dtype: "uint8";
    readonly shape: number[];
    readonly dimension: number;
    constructor(seq: ArrayLike<number> | ArrayBufferLike, shape?: number[]);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](_serializer: Serializer): unknown;
}
export declare class Int8NDArray extends Int8Array implements NDArrayType {
    readonly [__ndarray__] = true;
    readonly dtype: "int8";
    readonly shape: number[];
    readonly dimension: number;
    constructor(seq: ArrayLike<number> | ArrayBufferLike, shape?: number[]);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](_serializer: Serializer): unknown;
}
export declare class Uint16NDArray extends Uint16Array implements NDArrayType {
    readonly [__ndarray__] = true;
    readonly dtype: "uint16";
    readonly shape: number[];
    readonly dimension: number;
    constructor(seq: ArrayLike<number> | ArrayBufferLike, shape?: number[]);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](_serializer: Serializer): unknown;
}
export declare class Int16NDArray extends Int16Array implements NDArrayType {
    readonly [__ndarray__] = true;
    readonly dtype: "int16";
    readonly shape: number[];
    readonly dimension: number;
    constructor(seq: ArrayLike<number> | ArrayBufferLike, shape?: number[]);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](_serializer: Serializer): unknown;
}
export declare class Uint32NDArray extends Uint32Array implements NDArrayType {
    readonly [__ndarray__] = true;
    readonly dtype: "uint32";
    readonly shape: number[];
    readonly dimension: number;
    constructor(seq: ArrayLike<number> | ArrayBufferLike, shape?: number[]);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](_serializer: Serializer): unknown;
}
export declare class Int32NDArray extends Int32Array implements NDArrayType {
    readonly [__ndarray__] = true;
    readonly dtype: "int32";
    readonly shape: number[];
    readonly dimension: number;
    constructor(seq: ArrayLike<number> | ArrayBufferLike, shape?: number[]);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](_serializer: Serializer): unknown;
}
export declare class Float32NDArray extends Float32Array implements NDArrayType {
    readonly [__ndarray__] = true;
    readonly dtype: "float32";
    readonly shape: number[];
    readonly dimension: number;
    constructor(seq: ArrayLike<number> | ArrayBufferLike, shape?: number[]);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](_serializer: Serializer): unknown;
}
export declare class Float64NDArray extends Float64Array implements NDArrayType {
    readonly [__ndarray__] = true;
    readonly dtype: "float64";
    readonly shape: number[];
    readonly dimension: number;
    constructor(seq: ArrayLike<number> | ArrayBufferLike, shape?: number[]);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](_serializer: Serializer): unknown;
}
export declare type NDArray = Uint8NDArray | Int8NDArray | Uint16NDArray | Int16NDArray | Uint32NDArray | Int32NDArray | Float32NDArray | Float64NDArray;
export declare function is_NDArray(v: unknown): v is NDArray;
export declare type NDArrayTypes = {
    "uint8": {
        typed: Uint8Array;
        ndarray: Uint8NDArray;
    };
    "int8": {
        typed: Int8Array;
        ndarray: Int8NDArray;
    };
    "uint16": {
        typed: Uint16Array;
        ndarray: Uint16NDArray;
    };
    "int16": {
        typed: Int16Array;
        ndarray: Int16NDArray;
    };
    "uint32": {
        typed: Uint32Array;
        ndarray: Uint32NDArray;
    };
    "int32": {
        typed: Int32Array;
        ndarray: Int32NDArray;
    };
    "float32": {
        typed: Float32Array;
        ndarray: Float32NDArray;
    };
    "float64": {
        typed: Float64Array;
        ndarray: Float64NDArray;
    };
};
export declare function ndarray(array: ArrayBuffer | number[], options: {
    dtype: "uint8";
    shape: [number];
}): Uint8NDArray & Array1d;
export declare function ndarray(array: ArrayBuffer | number[], options: {
    dtype: "uint8";
    shape: [number, number];
}): Uint8NDArray & Array2d;
export declare function ndarray(array: ArrayBuffer | number[], options: {
    dtype: "uint32";
    shape: [number];
}): Uint32NDArray & Array1d;
export declare function ndarray(array: ArrayBuffer | number[], options: {
    dtype: "uint32";
    shape: [number, number];
}): Uint32NDArray & Array2d;
export declare function ndarray(array: ArrayBuffer | number[], options: {
    dtype: "float32";
    shape: [number];
}): Float32NDArray & Array1d;
export declare function ndarray(array: ArrayBuffer | number[], options: {
    dtype: "float32";
    shape: [number, number];
}): Float32NDArray & Array2d;
export declare function ndarray(array: ArrayBuffer | number[], options: {
    dtype: "float64";
    shape: [number];
}): Float64NDArray & Array1d;
export declare function ndarray(array: ArrayBuffer | number[], options: {
    dtype: "float64";
    shape: [number, number];
}): Float64NDArray & Array2d;
export declare function ndarray<K extends DataType = "float64">(array: ArrayBuffer | number[], options?: {
    dtype?: K;
    shape?: number[];
}): NDArrayTypes[K]["ndarray"];
export declare function ndarray<K extends DataType>(array: NDArrayTypes[K]["typed"], options?: {
    dtype?: K;
    shape?: number[];
}): NDArrayTypes[K]["ndarray"];
export {};
//# sourceMappingURL=ndarray.d.ts.map