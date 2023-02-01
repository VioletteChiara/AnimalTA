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
exports.build = exports.init = exports.isPlainObject = exports.isObject = exports.isString = void 0;
const cp = __importStar(require("child_process"));
const path_1 = require("path");
const sys_1 = require("./sys");
const compiler_1 = require("./compiler");
const linker_1 = require("./linker");
const styles_1 = require("./styles");
const preludes = __importStar(require("./prelude"));
const tsconfig_json = __importStar(require("./tsconfig.ext.json"));
const chalk_1 = __importDefault(require("chalk"));
const { cyan, magenta, red } = chalk_1.default;
const eslint_1 = require("eslint");
require("@typescript-eslint/eslint-plugin");
require("@typescript-eslint/parser");
const readline = __importStar(require("readline"));
const toString = Object.prototype.toString;
function isString(obj) {
    return toString.call(obj) === "[object String]";
}
exports.isString = isString;
function isObject(obj) {
    const tp = typeof obj;
    return tp === "function" || tp === "object" && !!obj;
}
exports.isObject = isObject;
function isPlainObject(obj) {
    return isObject(obj) && (obj.constructor == null || obj.constructor === Object);
}
exports.isPlainObject = isPlainObject;
function print(str) {
    console.log(str);
}
function npm_install(base_dir) {
    const npm = process.platform != "win32" ? "npm" : "npm.cmd";
    const { status } = cp.spawnSync(npm, ["install"], { stdio: "inherit", cwd: base_dir });
    if (status != null && status != 0) {
        print(`${cyan("npm install")} failed with exit code ${red(`${status}`)}.`);
        process.exit(status);
    }
}
function is_up_to_date(base_dir, file, metadata) {
    const contents = (0, sys_1.read)((0, path_1.join)(base_dir, file));
    if (contents == null)
        return false;
    const old_hash = metadata.signatures[file];
    if (old_hash == null)
        return false;
    const new_hash = (0, sys_1.hash)(contents);
    return old_hash == new_hash;
}
function needs_install(base_dir, metadata) {
    if (!(0, sys_1.directory_exists)((0, path_1.join)(base_dir, "node_modules")))
        return "New development environment.";
    else if (!is_up_to_date(base_dir, "package.json", metadata))
        return "package.json has changed.";
    else if (!is_up_to_date(base_dir, "package-lock.json", metadata))
        return "package-lock.json has changed.";
    else
        return null;
}
function lint(config_file, paths) {
    const engine = new eslint_1.CLIEngine({
        configFile: config_file,
        extensions: [".ts", ".js"],
    });
    const report = engine.executeOnFiles(paths);
    eslint_1.CLIEngine.outputFixes(report);
    const ok = report.errorCount == 0;
    if (!ok) {
        const formatter = engine.getFormatter();
        const output = formatter(report.results);
        for (const line of output.trim().split("\n"))
            print(line);
    }
    return ok;
}
async function init(base_dir, _bokehjs_dir, base_setup) {
    print(`Working directory: ${cyan(base_dir)}`);
    const setup = {
        interactive: !!base_setup.interactive,
        bokehjs_version: base_setup.bokehjs_version != null ? base_setup.bokehjs_version : base_setup.bokeh_version.split("-")[0],
        bokeh_version: base_setup.bokeh_version,
    };
    const paths = {
        bokeh_ext: (0, path_1.join)(base_dir, "bokeh.ext.json"),
        package: (0, path_1.join)(base_dir, "package.json"),
        package_lock: (0, path_1.join)(base_dir, "package-lock.json"),
        tsconfig: (0, path_1.join)(base_dir, "tsconfig.json"),
        index: (0, path_1.join)(base_dir, "index.ts"),
    };
    const is_extension = (0, sys_1.file_exists)(paths.bokeh_ext);
    if (is_extension) {
        print("Already a bokeh extension. Quitting.");
        return false;
    }
    function write_json(path, json) {
        (0, sys_1.write)(path, JSON.stringify(json, undefined, 2));
        print(`Wrote ${cyan(path)}`);
    }
    const bokeh_ext_json = {};
    write_json(paths.bokeh_ext, bokeh_ext_json);
    const package_json = {
        name: (0, path_1.basename)(base_dir),
        version: "0.0.1",
        description: "",
        license: "BSD-3-Clause",
        keywords: [],
        repository: {},
        dependencies: {
            "@bokeh/bokehjs": `^${setup.bokehjs_version}`,
        },
        devDependencies: {},
    };
    if (setup.interactive) {
        const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
        async function ask(question, default_value) {
            return new Promise((resolve, _reject) => {
                rl.question(`${question} `, (answer) => {
                    resolve(answer.length != 0 ? answer : default_value);
                });
            });
        }
        async function ask_yn(question) {
            const ret = await ask(`${question} [y/n]`, "y");
            switch (ret) {
                case "y":
                    return true;
                case "n":
                    return false;
                default: {
                    print(`${red("Invalid input")}. Assuming no.`);
                    return false;
                }
            }
        }
        if (await ask_yn(`Create ${cyan("package.json")}? This will allow you to specify external dependencies.`)) {
            const { name } = package_json;
            package_json.name = await ask(`  What's the extension's name? [${name}]`, name);
            const { version } = package_json;
            package_json.version = await ask(`  What's the extension's version? [${version}]`, version);
            const { description } = package_json;
            package_json.description = await ask(`  What's the extension's description? [${description}]`, description);
            write_json(paths.package, package_json);
        }
        if (await ask_yn(`Create ${cyan("tsconfig.json")}? This will allow for customized configuration and improved IDE experience.`)) {
            write_json(paths.tsconfig, tsconfig_json);
        }
        rl.close();
    }
    else {
        write_json(paths.package, package_json);
        write_json(paths.tsconfig, tsconfig_json);
    }
    (0, sys_1.write)(paths.index, "");
    print(`Created empty ${cyan("index.ts")}. This is the entry point of your extension.`);
    const rel = (0, path_1.relative)(process.cwd(), base_dir);
    print(`You can build your extension with ${magenta(`bokeh build ${rel}`)}`);
    print("All done.");
    return true;
}
exports.init = init;
async function build(base_dir, bokehjs_dir, base_setup) {
    print(`Working directory: ${cyan(base_dir)}`);
    const setup = {
        rebuild: !!base_setup.rebuild,
        bokeh_version: base_setup.bokeh_version,
    };
    const bokeh_ext_json_path = (0, path_1.join)(base_dir, "bokeh.ext.json");
    const bokeh_ext = (0, sys_1.read_json)(bokeh_ext_json_path);
    if (!isPlainObject(bokeh_ext)) {
        print("Not a bokeh extension. Quitting.");
        return false;
    }
    const metadata_path = (0, path_1.join)(base_dir, ".bokeh");
    const metadata = (() => {
        let obj = (0, sys_1.read_json)(metadata_path);
        if (obj == null)
            obj = {};
        if (obj.signatures == null)
            obj.signatures = {};
        return obj;
    })();
    if (metadata.bokeh_version != setup.bokeh_version) {
        print("Using different version of bokeh, rebuilding from scratch.");
        setup.rebuild = true;
    }
    const package_json_path = (0, path_1.join)(base_dir, "package.json");
    const package_lock_json_path = (0, path_1.join)(base_dir, "package-lock.json");
    const is_package = (0, sys_1.file_exists)(package_json_path);
    if (!is_package) {
        print(`${cyan(package_json_path)} doesn't exist. Not a npm package.`);
    }
    else {
        if (setup.rebuild) {
            print(`Running ${cyan("npm install")}.`);
            npm_install(base_dir);
        }
        else {
            const result = needs_install(base_dir, metadata);
            if (result != null) {
                print(`${result} Running ${cyan("npm install")}.`);
                npm_install(base_dir);
            }
        }
    }
    const tsconfig_path = (0, path_1.join)(base_dir, "tsconfig.json");
    const tsconfig = (() => {
        const preconfigure = {
            baseUrl: base_dir,
            paths: {
                "@bokehjs/*": [
                    (0, path_1.join)(bokehjs_dir, "js/lib/*"),
                    (0, path_1.join)(bokehjs_dir, "js/types/*"),
                ],
            },
        };
        if ((0, sys_1.file_exists)(tsconfig_path)) {
            print(`Using ${cyan(tsconfig_path)}`);
            return (0, compiler_1.read_tsconfig)(tsconfig_path, is_package ? undefined : preconfigure);
        }
        else
            return (0, compiler_1.parse_tsconfig)(tsconfig_json, base_dir, preconfigure);
    })();
    if ((0, compiler_1.is_failed)(tsconfig)) {
        print((0, compiler_1.report_diagnostics)(tsconfig.diagnostics).text);
        return false;
    }
    let success = true;
    const { files, options } = tsconfig;
    const dist_dir = (0, path_1.join)(base_dir, "dist");
    const lib_dir = options.outDir ?? dist_dir;
    const dts_dir = options.declarationDir ?? lib_dir;
    const styles_dir = (0, path_1.join)(base_dir, "styles");
    const css_dir = (0, path_1.join)(dist_dir, "css");
    print("Compiling styles");
    if (!await (0, styles_1.compile_styles)(styles_dir, css_dir))
        success = false;
    (0, styles_1.wrap_css_modules)(css_dir, lib_dir, dts_dir);
    const transformers = (0, compiler_1.default_transformers)(options);
    const host = (0, compiler_1.compiler_host)(new Map(), options, bokehjs_dir);
    print(`Compiling TypeScript (${magenta(`${files.length} files`)})`);
    const tsoutput = (0, compiler_1.compile_files)(files, options, transformers, host);
    if ((0, compiler_1.is_failed)(tsoutput)) {
        print((0, compiler_1.report_diagnostics)(tsoutput.diagnostics).text);
        if (options.noEmitOnError)
            return false;
    }
    const lint_config = (0, path_1.join)(base_dir, "eslint.json");
    if ((0, sys_1.file_exists)(lint_config)) {
        print("Linting sources");
        lint(lint_config, files);
    }
    const artifact = (0, path_1.basename)(base_dir);
    const bases = [lib_dir];
    if (is_package)
        bases.push((0, path_1.join)(base_dir, "node_modules"));
    const linker = new linker_1.Linker({
        entries: [(0, path_1.join)(lib_dir, "index.js")],
        bases,
        cache: (0, path_1.join)(dist_dir, `${artifact}.json`),
        excluded: (dep) => dep == "tslib" || dep.startsWith("@bokehjs/"),
        plugin: true,
        target: "ES2017",
    });
    print("Linking modules");
    if (!setup.rebuild)
        linker.load_cache();
    const { bundles, status } = await linker.link();
    if (!status)
        success = false;
    linker.store_cache();
    const outputs = [(0, path_1.join)(dist_dir, `${artifact}.js`)];
    const min_js = (js) => (0, sys_1.rename)(js, { ext: ".min.js" });
    const license = (() => {
        if (isPlainObject(bokeh_ext.license)) {
            if (isString(bokeh_ext.license.file)) {
                const license_path = (0, path_1.join)(base_dir, bokeh_ext.license.file);
                const text = (0, sys_1.read)(license_path);
                if (text != null)
                    return text;
                else
                    print(`Failed to license text from ${magenta(license_path)}`);
            }
            if (isString(bokeh_ext.license.text)) {
                return bokeh_ext.license.text;
            }
        }
        return null;
    })();
    const license_text = license ? `${preludes.comment(license)}\n` : "";
    const prelude_base = `${license_text}${preludes.plugin_prelude()}`;
    const prelude = { main: prelude_base, plugin: prelude_base };
    const postlude_base = preludes.plugin_postlude();
    const postlude = { main: postlude_base, plugin: postlude_base };
    // HACK {{{
    for (const bundle of bundles) {
        bundle.bases.push({});
    }
    // }}}
    function bundle(minified, outputs) {
        bundles
            .map((bundle) => bundle.assemble({ prelude, postlude, minified }))
            .map((artifact, i) => artifact.write(outputs[i]));
    }
    bundle(false, outputs);
    bundle(true, outputs.map(min_js));
    (0, sys_1.write)(metadata_path, JSON.stringify({
        bokeh_version: setup.bokeh_version,
        signatures: {
            "package.json": (0, sys_1.hash_file)(package_json_path),
            "package-lock.json": (0, sys_1.hash_file)(package_lock_json_path),
            "tsconfig.json": (0, sys_1.hash_file)(tsconfig_path),
        },
    }));
    print(`Output written to ${cyan(dist_dir)}`);
    print("All done.");
    return !(0, compiler_1.is_failed)(tsoutput) && success;
}
exports.build = build;
//# sourceMappingURL=build.js.map