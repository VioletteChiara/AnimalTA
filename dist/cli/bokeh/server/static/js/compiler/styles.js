"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.wrap_css_modules = exports.compile_styles = void 0;
const path_1 = require("path");
const less_1 = __importDefault(require("less"));
const chalk_1 = __importDefault(require("chalk"));
const sys_1 = require("./sys");
async function compile_styles(styles_dir, css_dir) {
    let success = true;
    for (const src of (0, sys_1.scan)(styles_dir, [".less", ".css"])) {
        if ((0, path_1.basename)(src).startsWith("_"))
            continue;
        try {
            const style = (0, sys_1.read)(src);
            const { css } = await less_1.default.render(style, { filename: src });
            const dst = (0, sys_1.rename)(src, { base: styles_dir, dir: css_dir, ext: ".css" });
            (0, sys_1.write)(dst, css);
        }
        catch (error) {
            success = false;
            console.log(`${chalk_1.default.red("\u2717")} failed to compile ${chalk_1.default.magenta(src)}:`);
            console.log(`${error}`);
        }
    }
    return success;
}
exports.compile_styles = compile_styles;
function wrap_css_modules(css_dir, js_dir, dts_dir) {
    for (const css_path of (0, sys_1.scan)(css_dir, [".css"])) {
        const js = `\
const css = \`\n${(0, sys_1.read)(css_path)}\`;
export default css;
`;
        const dts = `\
declare const css: string;
export default css;
`;
        const sub_path = (0, path_1.relative)(css_dir, css_path);
        (0, sys_1.write)(`${(0, path_1.join)(js_dir, "styles", sub_path)}.js`, js);
        (0, sys_1.write)(`${(0, path_1.join)(dts_dir, "styles", sub_path)}.d.ts`, dts);
    }
}
exports.wrap_css_modules = wrap_css_modules;
//# sourceMappingURL=styles.js.map