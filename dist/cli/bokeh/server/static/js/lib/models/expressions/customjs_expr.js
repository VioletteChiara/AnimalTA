var _a;
import { HasProps } from "../../core/has_props";
import { Expression } from "./expression";
import { GeneratorFunction } from "../../core/types";
import { repeat } from "../../core/util/array";
import { keys, values } from "../../core/util/object";
import { use_strict } from "../../core/util/string";
import { isArray, isTypedArray, isIterable } from "../../core/util/types";
export class CustomJSExpr extends Expression {
    constructor(attrs) {
        super(attrs);
    }
    connect_signals() {
        super.connect_signals();
        for (const value of values(this.args)) {
            if (value instanceof HasProps) {
                value.change.connect(() => {
                    this._result.clear();
                    this.change.emit();
                });
            }
        }
    }
    get names() {
        return keys(this.args);
    }
    get values() {
        return values(this.args);
    }
    get func() {
        const code = use_strict(this.code);
        return new GeneratorFunction(...this.names, code);
    }
    _v_compute(source) {
        const generator = this.func.apply(source, this.values);
        let result = generator.next();
        if (result.done && result.value !== undefined) {
            const { value } = result;
            if (isArray(value) || isTypedArray(value))
                return value;
            else if (isIterable(value))
                return [...value];
            else
                return repeat(value, source.length);
        }
        else {
            const array = [];
            do {
                array.push(result.value);
                result = generator.next();
            } while (!result.done);
            return array;
        }
    }
}
_a = CustomJSExpr;
CustomJSExpr.__name__ = "CustomJSExpr";
(() => {
    _a.define(({ Unknown, String, Dict }) => ({
        args: [Dict(Unknown), {}],
        code: [String, ""],
    }));
})();
//# sourceMappingURL=customjs_expr.js.map