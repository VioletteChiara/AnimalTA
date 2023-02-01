var _a;
import { Model } from "../../model";
export class Range extends Model {
    constructor(attrs) {
        super(attrs);
        this.have_updated_interactively = false;
    }
    get is_reversed() {
        return this.start > this.end;
    }
    get is_valid() {
        return isFinite(this.min) && isFinite(this.max);
    }
    get span() {
        return Math.abs(this.end - this.start);
    }
}
_a = Range;
Range.__name__ = "Range";
(() => {
    _a.define(({ Number, Tuple, Or, Auto, Nullable }) => ({
        bounds: [Nullable(Or(Tuple(Nullable(Number), Nullable(Number)), Auto)), null],
        min_interval: [Nullable(Number), null],
        max_interval: [Nullable(Number), null],
    }));
    _a.internal(({ Array, AnyRef }) => ({
        plots: [Array(AnyRef()), []],
    }));
})();
//# sourceMappingURL=range.js.map