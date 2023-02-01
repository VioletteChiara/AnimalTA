import { Attrs } from "../types";
export declare type Struct = {
    id: string;
    type: string;
    subtype?: string;
    attributes: Attrs;
};
export declare type Ref = {
    id: string;
};
export declare function is_ref(arg: unknown): arg is Ref;
//# sourceMappingURL=refs.d.ts.map