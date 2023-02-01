import { TSOutput, Inputs, Outputs } from "./compiler";
export declare function compile_typescript(base_dir: string, inputs: Inputs, bokehjs_dir: string): {
    outputs?: Outputs;
} & TSOutput;
export declare function compile_and_resolve_deps(input: {
    code: string;
    lang: string;
    file: string;
    bokehjs_dir: string;
}): Promise<{
    error: string;
    code?: undefined;
    deps?: undefined;
} | {
    code: string;
    error?: undefined;
    deps?: undefined;
} | {
    code: string;
    deps: string[];
    error?: undefined;
}>;
//# sourceMappingURL=compile.d.ts.map