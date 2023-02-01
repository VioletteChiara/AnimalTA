"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    Object.defineProperty(o, k2, { enumerable: true, get: function() { return m[k]; } });
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.compile_and_resolve_deps = exports.compile_typescript = void 0;
const path = __importStar(require("path"));
const ts = __importStar(require("typescript"));
const less_1 = __importDefault(require("less"));
const compiler_1 = require("./compiler");
const sys_1 = require("./sys");
const transforms = __importStar(require("./transforms"));
const tsconfig_json = __importStar(require("./tsconfig.ext.json"));
function parse_patched_tsconfig(base_dir, preconfigure) {
    // XXX: silence the config validator. We are providing inputs through `inputs` argument anyway.
    const json = { ...tsconfig_json, include: undefined, files: ["dummy.ts"] };
    return (0, compiler_1.parse_tsconfig)(json, base_dir, preconfigure);
}
function compile_typescript(base_dir, inputs, bokehjs_dir) {
    const preconfigure = {
        module: ts.ModuleKind.CommonJS,
        paths: {
            "*": [
                path.join(bokehjs_dir, "js/lib/*"),
                path.join(bokehjs_dir, "js/types/*"),
            ],
        },
        outDir: undefined,
    };
    const tsconfig = parse_patched_tsconfig(base_dir, preconfigure);
    if (tsconfig.diagnostics != null)
        return { diagnostics: tsconfig.diagnostics };
    const host = (0, compiler_1.compiler_host)(inputs, tsconfig.options, bokehjs_dir);
    const transformers = (0, compiler_1.default_transformers)(tsconfig.options);
    const outputs = new Map();
    host.writeFile = (name, data) => {
        outputs.set(name, data);
    };
    const files = [...inputs.keys()];
    return { outputs, ...(0, compiler_1.compile_files)(files, tsconfig.options, transformers, host) };
}
exports.compile_typescript = compile_typescript;
function compile_javascript(base_dir, file, code) {
    const tsconfig = parse_patched_tsconfig(base_dir, {});
    if (tsconfig.diagnostics != null)
        return { diagnostics: tsconfig.diagnostics };
    const { outputText, diagnostics } = ts.transpileModule(code, {
        fileName: file,
        reportDiagnostics: true,
        compilerOptions: {
            target: tsconfig.options.target,
            module: ts.ModuleKind.CommonJS,
        },
    });
    return { output: outputText, diagnostics };
}
function normalize(path) {
    return path.replace(/\\/g, "/");
}
async function compile_and_resolve_deps(input) {
    const { file, lang, bokehjs_dir } = input;
    const { code } = input;
    let output;
    switch (lang) {
        case "typescript":
            const inputs = new Map([[normalize(file), code]]);
            const { outputs, diagnostics } = compile_typescript(".", inputs, bokehjs_dir);
            if (diagnostics != null && diagnostics.length != 0) {
                const failure = (0, compiler_1.report_diagnostics)(diagnostics);
                return { error: failure.text };
            }
            else {
                const js_file = normalize((0, sys_1.rename)(file, { ext: ".js" }));
                output = outputs.get(js_file);
            }
            break;
        case "javascript": {
            const result = compile_javascript(".", file, code);
            if (result.diagnostics != null && result.diagnostics.length != 0) {
                const failure = (0, compiler_1.report_diagnostics)(result.diagnostics);
                return { error: failure.text };
            }
            else {
                output = result.output;
            }
            break;
        }
        case "less":
            try {
                const { css } = await less_1.default.render(code, { filename: file, compress: true });
                return { code: css };
            }
            catch (error) {
                return { error: `${error}` };
            }
        default:
            throw new Error(`unsupported input type: ${lang}`);
    }
    const source = ts.createSourceFile(file, output, ts.ScriptTarget.ES5, true, ts.ScriptKind.JS);
    const deps = transforms.collect_deps(source);
    return { code: output, deps };
}
exports.compile_and_resolve_deps = compile_and_resolve_deps;
//# sourceMappingURL=compile.js.map