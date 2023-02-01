import { Path } from "./sys";
import "@typescript-eslint/eslint-plugin";
import "@typescript-eslint/parser";
export declare function isString(obj: unknown): obj is string;
export declare function isObject(obj: unknown): obj is object;
export declare function isPlainObject<T>(obj: unknown): obj is {
    [key: string]: T;
};
export declare type InitOptions = {
    interactive?: boolean;
    bokehjs_version?: string;
    bokeh_version: string;
};
export declare function init(base_dir: Path, _bokehjs_dir: Path, base_setup: InitOptions): Promise<boolean>;
export declare type BuildOptions = {
    rebuild?: boolean;
    bokeh_version: string;
};
export declare function build(base_dir: Path, bokehjs_dir: Path, base_setup: BuildOptions): Promise<boolean>;
//# sourceMappingURL=build.d.ts.map