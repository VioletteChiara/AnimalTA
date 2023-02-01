var _a;
import { Transform } from "../transforms/transform";
import { Range } from "../ranges/range";
import { Range1d } from "../ranges/range1d";
import { ScreenArray } from "../../core/types";
export class Scale extends Transform {
    constructor(attrs) {
        super(attrs);
    }
    compute(x) {
        return this.s_compute(x);
    }
    v_compute(xs) {
        const result = new ScreenArray(xs.length);
        const { s_compute } = this;
        for (let i = 0; i < xs.length; i++) {
            result[i] = s_compute(xs[i]);
        }
        return result;
    }
    invert(sx) {
        return this.s_invert(sx);
    }
    v_invert(sxs) {
        const result = new Float64Array(sxs.length);
        const { s_invert } = this;
        for (let i = 0; i < sxs.length; i++) {
            result[i] = s_invert(sxs[i]);
        }
        return result;
    }
    r_compute(x0, x1) {
        const { s_compute } = this;
        if (this.target_range.is_reversed)
            return [s_compute(x1), s_compute(x0)];
        else
            return [s_compute(x0), s_compute(x1)];
    }
    r_invert(sx0, sx1) {
        const { s_invert } = this;
        if (this.target_range.is_reversed)
            return [s_invert(sx1), s_invert(sx0)];
        else
            return [s_invert(sx0), s_invert(sx1)];
    }
}
_a = Scale;
Scale.__name__ = "Scale";
(() => {
    _a.internal(({ Ref }) => ({
        source_range: [Ref(Range)],
        target_range: [Ref(Range1d)],
    }));
})();
//# sourceMappingURL=scale.js.map