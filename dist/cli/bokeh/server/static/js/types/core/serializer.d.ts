import { Ref, Struct } from "./util/refs";
export declare type SerializableType = null | boolean | number | string | Serializable | SerializableType[] | {
    [key: string]: SerializableType;
};
export declare const serialize: unique symbol;
export interface Serializable {
    [serialize](serializer: Serializer): unknown;
}
export declare type SerializableOf<T extends SerializableType> = T extends Serializable ? ReturnType<T[typeof serialize]> : T extends SerializableType[] ? SerializableOf<T[number]>[] : unknown;
export declare class SerializationError extends Error {
}
export declare class Serializer {
    private readonly _references;
    private readonly _definitions;
    private readonly _refmap;
    readonly include_defaults: boolean;
    constructor(options?: {
        include_defaults?: boolean;
    });
    get_ref(obj: unknown): Ref | undefined;
    add_ref(obj: unknown, ref: Ref): void;
    add_def(obj: unknown, def: Struct): void;
    get objects(): Set<unknown>;
    get references(): Set<Ref>;
    get definitions(): Set<Struct>;
    resolve_ref(ref: Ref): Struct | undefined;
    remove_ref(obj: unknown): boolean;
    remove_def(obj: unknown): boolean;
    to_serializable<T extends SerializableType>(obj: T): SerializableOf<T>;
    to_serializable(obj: unknown): unknown;
}
//# sourceMappingURL=serializer.d.ts.map