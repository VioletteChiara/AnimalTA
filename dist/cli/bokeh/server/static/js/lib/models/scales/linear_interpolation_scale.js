var _a;
import { Scale } from "./scale";
import { LinearScale } from "./linear_scale";
import { map, left_edge_index } from "../../core/util/arrayable";
export class LinearInterpolationScale extends Scale {
    constructor(attrs) {
        super(attrs);
    }
    connect_signals() {
        super.connect_signals();
        const { source_range, target_range } = this.properties;
        this.on_change([source_range, target_range], () => {
            this.linear_scale = new LinearScale({
                source_range: this.source_range,
                target_range: this.target_range,
            });
        });
    }
    get s_compute() {
        throw new Error("not implemented");
    }
    get s_invert() {
        throw new Error("not implemented");
    }
    compute(x) {
        return x;
    }
    v_compute(vs) {
        const { binning } = this;
        const { start, end } = this.source_range;
        const min_val = start;
        const max_val = end;
        const n = binning.length;
        const step = (end - start) / (n - 1);
        const mapping = new Float64Array(n);
        for (let i = 0; i < n; i++) {
            mapping[i] = start + i * step;
        }
        const vvs = map(vs, (v) => {
            if (v < min_val)
                return min_val;
            if (v > max_val)
                return max_val;
            const k = left_edge_index(v, binning);
            if (k == -1)
                return min_val;
            if (k >= n - 1)
                return max_val;
            const b0 = binning[k];
            const b1 = binning[k + 1];
            const c = (v - b0) / (b1 - b0);
            const m0 = mapping[k];
            const m1 = mapping[k + 1];
            return m0 + c * (m1 - m0);
        });
        return this.linear_scale.v_compute(vvs);
    }
    invert(xprime) {
        return xprime;
    }
    v_invert(xprimes) {
        return new Float64Array(xprimes);
    }
}
_a = LinearInterpolationScale;
LinearInterpolationScale.__name__ = "LinearInterpolationScale";
(() => {
    _a.internal(({ Arrayable, Ref }) => ({
        binning: [Arrayable],
        linear_scale: [
            Ref(LinearScale),
            (self) => new LinearScale({
                source_range: self.source_range,
                target_range: self.target_range,
            }),
        ],
    }));
})();
//# sourceMappingURL=linear_interpolation_scale.js.map