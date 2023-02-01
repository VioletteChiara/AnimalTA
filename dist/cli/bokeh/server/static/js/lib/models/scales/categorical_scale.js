import { Scale } from "./scale";
import { LinearScale } from "./linear_scale";
const { _linear_compute_state } = LinearScale.prototype;
export class CategoricalScale extends Scale {
    constructor(attrs) {
        super(attrs);
    }
    get s_compute() {
        const [factor, offset] = _linear_compute_state.call(this);
        const range = this.source_range;
        return (x) => factor * range.synthetic(x) + offset;
    }
    get s_invert() {
        const [factor, offset] = _linear_compute_state.call(this);
        return (sx) => (sx - offset) / factor;
    }
}
CategoricalScale.__name__ = "CategoricalScale";
//# sourceMappingURL=categorical_scale.js.map