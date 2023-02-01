var _a;
import { Transform } from "./transform";
import { Range } from "../ranges/range";
import { FactorRange } from "../ranges/factor_range";
import { infer_type } from "../../core/types";
import { isNumber, isArrayableOf } from "../../core/util/types";
import { unreachable } from "../../core/util/assert";
export class RangeTransform extends Transform {
    constructor(attrs) {
        super(attrs);
    }
    v_compute(xs0) {
        let xs;
        if (this.range instanceof FactorRange)
            xs = this.range.v_synthetic(xs0);
        else if (isArrayableOf(xs0, isNumber))
            xs = xs0;
        else
            unreachable();
        const result = new (infer_type(xs))(xs.length);
        for (let i = 0; i < xs.length; i++) {
            const x = xs[i];
            result[i] = this._compute(x);
        }
        return result;
    }
    compute(x) {
        if (this.range instanceof FactorRange)
            return this._compute(this.range.synthetic(x));
        else if (isNumber(x))
            return this._compute(x);
        else
            unreachable();
    }
}
_a = RangeTransform;
RangeTransform.__name__ = "RangeTransform";
(() => {
    _a.define(({ Ref, Nullable }) => ({
        range: [Nullable(Ref(Range)), null],
    }));
})();
//# sourceMappingURL=range_transform.js.map