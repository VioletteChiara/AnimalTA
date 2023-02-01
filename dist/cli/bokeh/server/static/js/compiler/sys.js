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
exports.read_json = exports.hash_file = exports.hash = exports.rename = exports.directory_exists = exports.file_exists = exports.write = exports.read = exports.glob = exports.scan = void 0;
const ts = __importStar(require("typescript"));
const crypto_1 = __importDefault(require("crypto"));
const path_1 = require("path");
function scan(path, extensions, exclude, include, depth) {
    return ts.sys.readDirectory(path, extensions, exclude, include, depth).map((p) => (0, path_1.normalize)(p));
}
exports.scan = scan;
function glob(...patterns) {
    return scan(".", undefined, undefined, patterns);
}
exports.glob = glob;
exports.read = ts.sys.readFile;
exports.write = ts.sys.writeFile;
exports.file_exists = ts.sys.fileExists;
exports.directory_exists = ts.sys.directoryExists;
function rename(path, options) {
    let { dir, name, ext } = (0, path_1.parse)(path);
    if (options.dir != null) {
        if (options.base != null)
            dir = dir.replace(options.base, options.dir);
        else
            dir = options.dir;
    }
    if (options.name != null)
        name = options.name(name);
    if (options.ext != null)
        ext = options.ext;
    return (0, path_1.format)({ dir, name, ext });
}
exports.rename = rename;
function hash(data) {
    return crypto_1.default.createHash("sha256").update(data).digest("hex");
}
exports.hash = hash;
function hash_file(path) {
    const contents = (0, exports.read)(path);
    return contents != null ? hash(contents) : null;
}
exports.hash_file = hash_file;
function read_json(path) {
    const data = (0, exports.read)(path);
    if (data == null)
        return undefined;
    else {
        try {
            return JSON.parse(data);
        }
        catch {
            return undefined;
        }
    }
}
exports.read_json = read_json;
//# sourceMappingURL=sys.js.map