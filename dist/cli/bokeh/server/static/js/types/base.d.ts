import { HasProps } from "./core/has_props";
export declare const overrides: {
    [key: string]: typeof HasProps;
};
export interface Models {
    (name: string): typeof HasProps;
    get(name: string): typeof HasProps | undefined;
    register(name: string, model: typeof HasProps): void;
    unregister(name: string): void;
    register_models(models: {
        [key: string]: unknown;
    } | unknown[] | null | undefined, force?: boolean, errorFn?: (name: string) => void): void;
    registered_names(): string[];
}
export declare const Models: Models;
export declare const register_models: (models: unknown[] | {
    [key: string]: unknown;
} | null | undefined, force?: boolean | undefined, errorFn?: ((name: string) => void) | undefined) => void;
export declare class ModelResolver {
    protected _known_models: Map<string, typeof HasProps>;
    get(name: string): typeof HasProps;
    get<T>(name: string, or_else: T): (typeof HasProps) | T;
    register(model: typeof HasProps): void;
}
//# sourceMappingURL=base.d.ts.map