"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const yargs_1 = require("yargs");
const path_1 = require("path");
const sys_1 = require("./sys");
const build_1 = require("./build");
const compile_1 = require("./compile");
async function read_stdin() {
    const stdin = process.stdin;
    stdin.setEncoding("utf-8");
    stdin.resume();
    let data = "";
    for await (const chunk of stdin) {
        data += chunk;
    }
    return data;
}
function reply(data) {
    process.stdout.write(JSON.stringify(data));
    process.stdout.write("\n");
}
async function compile() {
    if (yargs_1.argv.file != null) {
        const input = {
            code: yargs_1.argv.code != null ? yargs_1.argv.code : (0, sys_1.read)(yargs_1.argv.file),
            lang: yargs_1.argv.lang ?? "typescript",
            file: yargs_1.argv.file,
            bokehjs_dir: yargs_1.argv.bokehjsDir ?? "./build", // this is what bokeh.settings defaults to
        };
        return await (0, compile_1.compile_and_resolve_deps)(input);
    }
    else {
        const input = JSON.parse(await read_stdin());
        return await (0, compile_1.compile_and_resolve_deps)(input);
    }
}
async function main() {
    const cmd = yargs_1.argv._[0];
    if (cmd == "build") {
        try {
            const base_dir = (0, path_1.resolve)(yargs_1.argv.baseDir);
            const bokehjs_dir = (0, path_1.resolve)(yargs_1.argv.bokehjsDir);
            const rebuild = yargs_1.argv.rebuild;
            const bokeh_version = yargs_1.argv.bokehVersion;
            const result = await (0, build_1.build)(base_dir, bokehjs_dir, { rebuild, bokeh_version });
            process.exit(result ? 0 : 1);
        }
        catch (error) {
            const msg = error instanceof Error && error.stack ? error.stack : `${error}`;
            console.log(msg);
            process.exit(1);
        }
    }
    else if (cmd == "init") {
        try {
            const base_dir = (0, path_1.resolve)(yargs_1.argv.baseDir);
            const bokehjs_dir = (0, path_1.resolve)(yargs_1.argv.bokehjsDir);
            const interactive = yargs_1.argv.interactive;
            const bokehjs_version = yargs_1.argv.bokehjsVersion;
            const bokeh_version = yargs_1.argv.bokehVersion;
            const result = await (0, build_1.init)(base_dir, bokehjs_dir, { interactive, bokehjs_version, bokeh_version });
            process.exit(result ? 0 : 1);
        }
        catch (error) {
            const msg = error instanceof Error && error.stack ? error.stack : `${error}`;
            console.log(msg);
            process.exit(1);
        }
    }
    else {
        try {
            reply(await compile());
        }
        catch (error) {
            const msg = error instanceof Error && error.stack ? error.stack : `${error}`;
            reply({ error: msg });
        }
    }
}
main();
//# sourceMappingURL=main.js.map