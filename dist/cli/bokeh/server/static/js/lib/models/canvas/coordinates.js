var _a, _b;
import { map } from "../../core/util/arrayable";
import { Model } from "../../model";
import { Scale } from "../scales/scale";
import { LinearScale } from "../scales/linear_scale";
import { LogScale } from "../scales/log_scale";
import { CategoricalScale } from "../scales/categorical_scale";
import { Range } from "../ranges/range";
import { DataRange1d } from "../ranges/data_range1d";
import { FactorRange } from "../ranges/factor_range";
export class CoordinateTransform {
    constructor(x_scale, y_scale) {
        this.x_scale = x_scale;
        this.y_scale = y_scale;
        this.x_source = this.x_scale.source_range;
        this.y_source = this.y_scale.source_range;
        this.ranges = [this.x_source, this.y_source];
        this.scales = [this.x_scale, this.y_scale];
    }
    map_to_screen(xs, ys) {
        const sxs = this.x_scale.v_compute(xs);
        const sys = this.y_scale.v_compute(ys);
        return [sxs, sys];
    }
    map_from_screen(sxs, sys) {
        const xs = this.x_scale.v_invert(sxs);
        const ys = this.y_scale.v_invert(sys);
        return [xs, ys];
    }
}
CoordinateTransform.__name__ = "CoordinateTransform";
export class CoordinateMapping extends Model {
    constructor(attrs) {
        super(attrs);
    }
    get x_ranges() {
        return new Map([["default", this.x_source]]);
    }
    get y_ranges() {
        return new Map([["default", this.y_source]]);
    }
    _get_scale(range, scale, target) {
        const factor_range = range instanceof FactorRange;
        const categorical_scale = scale instanceof CategoricalScale;
        if (factor_range != categorical_scale) {
            throw new Error(`Range ${range.type} is incompatible is Scale ${scale.type}`);
        }
        if (scale instanceof LogScale && range instanceof DataRange1d)
            range.scale_hint = "log";
        const derived_scale = scale.clone();
        derived_scale.setv({ source_range: range, target_range: target });
        return derived_scale;
    }
    get_transform(frame) {
        const { x_source, x_scale, x_target } = this;
        const x_source_scale = this._get_scale(x_source, x_scale, x_target);
        const { y_source, y_scale, y_target } = this;
        const y_source_scale = this._get_scale(y_source, y_scale, y_target);
        const xscale = new CompositeScale({
            source_scale: x_source_scale, source_range: x_source_scale.source_range,
            target_scale: frame.x_scale, target_range: frame.x_target,
        });
        const yscale = new CompositeScale({
            source_scale: y_source_scale, source_range: y_source_scale.source_range,
            target_scale: frame.y_scale, target_range: frame.y_target,
        });
        return new CoordinateTransform(xscale, yscale);
    }
}
_a = CoordinateMapping;
CoordinateMapping.__name__ = "CoordinateMapping";
(() => {
    _a.define(({ Ref }) => ({
        x_source: [Ref(Range), () => new DataRange1d()],
        y_source: [Ref(Range), () => new DataRange1d()],
        x_scale: [Ref(Scale), () => new LinearScale()],
        y_scale: [Ref(Scale), () => new LinearScale()],
        x_target: [Ref(Range)],
        y_target: [Ref(Range)],
    }));
})();
export class CompositeScale extends Scale {
    constructor(attrs) {
        super(attrs);
    }
    get s_compute() {
        const source_compute = this.source_scale.s_compute;
        const target_compute = this.target_scale.s_compute;
        return (x) => target_compute(source_compute(x));
    }
    get s_invert() {
        const source_invert = this.source_scale.s_invert;
        const target_invert = this.target_scale.s_invert;
        return (sx) => source_invert(target_invert(sx));
    }
    compute(x) {
        return this.s_compute(x);
    }
    v_compute(xs) {
        const { s_compute } = this;
        return map(xs, s_compute); // XXX
    }
    invert(sx) {
        return this.s_invert(sx);
    }
    v_invert(sxs) {
        const { s_invert } = this;
        return map(sxs, s_invert); // XXX
    }
}
_b = CompositeScale;
CompositeScale.__name__ = "CompositeScale";
(() => {
    _b.internal(({ Ref }) => ({
        source_scale: [Ref(Scale)],
        target_scale: [Ref(Scale)],
    }));
})();
//# sourceMappingURL=coordinates.js.map