var _a;
import { Interpolator } from "./interpolator";
import { StepMode } from "../../core/enums";
import { map, min, find_index, find_last_index } from "../../core/util/array";
export class StepInterpolator extends Interpolator {
    constructor(attrs) {
        super(attrs);
    }
    compute(x) {
        this.sort(false);
        if (this.clip) {
            if (x < this._x_sorted[0] || x > this._x_sorted[this._x_sorted.length - 1])
                return NaN;
        }
        else {
            if (x < this._x_sorted[0])
                return this._y_sorted[0];
            if (x > this._x_sorted[this._x_sorted.length - 1])
                return this._y_sorted[this._y_sorted.length - 1];
        }
        let ind;
        switch (this.mode) {
            case "after": {
                ind = find_last_index(this._x_sorted, num => x >= num);
                break;
            }
            case "before": {
                ind = find_index(this._x_sorted, num => x <= num);
                break;
            }
            case "center": {
                const diffs = map(this._x_sorted, (tx) => Math.abs(tx - x));
                const mdiff = min(diffs);
                ind = find_index(diffs, num => mdiff === num);
                break;
            }
            default:
                throw new Error(`unknown mode: ${this.mode}`);
        }
        return ind != -1 ? this._y_sorted[ind] : NaN;
    }
}
_a = StepInterpolator;
StepInterpolator.__name__ = "StepInterpolator";
(() => {
    _a.define(() => ({
        mode: [StepMode, "after"],
    }));
})();
//# sourceMappingURL=step_interpolator.js.map