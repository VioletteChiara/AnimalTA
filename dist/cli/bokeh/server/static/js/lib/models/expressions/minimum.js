var _a;
import { ScalarExpression } from "./expression";
import { min } from "../../core/util/array";
export class Minimum extends ScalarExpression {
    constructor(attrs) {
        super(attrs);
    }
    _compute(source) {
        const column = source.data[this.field] ?? [];
        return Math.min(this.initial ?? Infinity, min(column));
    }
}
_a = Minimum;
Minimum.__name__ = "Minimum";
(() => {
    _a.define(({ Number, String, Nullable }) => ({
        field: [String],
        initial: [Nullable(Number), null], // TODO: Infinity
    }));
})();
//# sourceMappingURL=minimum.js.map