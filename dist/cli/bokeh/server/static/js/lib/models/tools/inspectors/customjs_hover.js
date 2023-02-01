var _a;
import { Model } from "../../../model";
import { keys, values } from "../../../core/util/object";
import { use_strict } from "../../../core/util/string";
export class CustomJSHover extends Model {
    constructor(attrs) {
        super(attrs);
    }
    get values() {
        return values(this.args);
    }
    /*protected*/ _make_code(valname, formatname, varsname, fn) {
        // this relies on keys(args) and values(args) returning keys and values
        // in the same order
        return new Function(...keys(this.args), valname, formatname, varsname, use_strict(fn));
    }
    format(value, format, special_vars) {
        const formatter = this._make_code("value", "format", "special_vars", this.code);
        return formatter(...this.values, value, format, special_vars);
    }
}
_a = CustomJSHover;
CustomJSHover.__name__ = "CustomJSHover";
(() => {
    _a.define(({ Unknown, String, Dict }) => ({
        args: [Dict(Unknown), {}],
        code: [String, ""],
    }));
})();
//# sourceMappingURL=customjs_hover.js.map