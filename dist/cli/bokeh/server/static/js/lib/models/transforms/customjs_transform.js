var _a;
import { Transform } from "./transform";
import { keys, values } from "../../core/util/object";
import { use_strict } from "../../core/util/string";
export class CustomJSTransform extends Transform {
    constructor(attrs) {
        super(attrs);
    }
    get names() {
        return keys(this.args);
    }
    get values() {
        return values(this.args);
    }
    _make_transform(name, func) {
        return new Function(...this.names, name, use_strict(func));
    }
    get scalar_transform() {
        return this._make_transform("x", this.func);
    }
    get vector_transform() {
        return this._make_transform("xs", this.v_func);
    }
    compute(x) {
        return this.scalar_transform(...this.values, x);
    }
    v_compute(xs) {
        return this.vector_transform(...this.values, xs);
    }
}
_a = CustomJSTransform;
CustomJSTransform.__name__ = "CustomJSTransform";
(() => {
    _a.define(({ Unknown, String, Dict }) => ({
        args: [Dict(Unknown), {}],
        func: [String, ""],
        v_func: [String, ""],
    }));
})();
//# sourceMappingURL=customjs_transform.js.map