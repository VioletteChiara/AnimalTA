var _a;
import { ScalarExpression } from "./expression";
import { max } from "../../core/util/array";
export class Maximum extends ScalarExpression {
    constructor(attrs) {
        super(attrs);
    }
    _compute(source) {
        const column = source.data[this.field] ?? [];
        return Math.max(this.initial ?? -Infinity, max(column));
    }
}
_a = Maximum;
Maximum.__name__ = "Maximum";
(() => {
    _a.define(({ Number, String, Nullable }) => ({
        field: [String],
        initial: [Nullable(Number), null], // TODO: -Infinity
    }));
})();
//# sourceMappingURL=maximum.js.map