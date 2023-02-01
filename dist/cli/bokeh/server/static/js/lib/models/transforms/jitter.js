var _a;
import { RangeTransform } from "./range_transform";
import { FactorRange } from "../ranges/factor_range";
import { Distribution } from "../../core/enums";
import { isNumber, isArrayableOf } from "../../core/util/types";
import { map } from "../../core/util/arrayable";
import * as bokeh_math from "../../core/util/math";
import { unreachable } from "../../core/util/assert";
export class Jitter extends RangeTransform {
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
        const xs_length = xs.length;
        if (this.previous_offsets?.length != xs_length) {
            this.previous_offsets = new Array(xs_length);
            this.previous_offsets = map(this.previous_offsets, () => this._compute());
        }
        const offsets = this.previous_offsets;
        return map(xs, (xs, i) => offsets[i] + xs);
    }
    _compute() {
        switch (this.distribution) {
            case "uniform":
                return this.mean + (bokeh_math.random() - 0.5) * this.width;
            case "normal":
                return bokeh_math.rnorm(this.mean, this.width);
        }
    }
}
_a = Jitter;
Jitter.__name__ = "Jitter";
(() => {
    _a.define(({ Number }) => ({
        mean: [Number, 0],
        width: [Number, 1],
        distribution: [Distribution, "uniform"],
    }));
})();
//# sourceMappingURL=jitter.js.map