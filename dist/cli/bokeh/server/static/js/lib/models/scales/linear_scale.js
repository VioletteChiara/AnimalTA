import { ContinuousScale } from "./continuous_scale";
export class LinearScale extends ContinuousScale {
    constructor(attrs) {
        super(attrs);
    }
    get s_compute() {
        const [factor, offset] = this._linear_compute_state();
        return (x) => factor * x + offset;
    }
    get s_invert() {
        const [factor, offset] = this._linear_compute_state();
        return (sx) => (sx - offset) / factor;
    }
    /*protected*/ _linear_compute_state() {
        //
        //  (t1 - t0)       (t1 - t0)
        //  --------- * x - --------- * s0 + t0
        //  (s1 - s0)       (s1 - s0)
        //
        // [  factor  ]     [    offset    ]
        //
        const source_start = this.source_range.start;
        const source_end = this.source_range.end;
        const target_start = this.target_range.start;
        const target_end = this.target_range.end;
        const factor = (target_end - target_start) / (source_end - source_start);
        const offset = -(factor * source_start) + target_start;
        return [factor, offset];
    }
}
LinearScale.__name__ = "LinearScale";
//# sourceMappingURL=linear_scale.js.map