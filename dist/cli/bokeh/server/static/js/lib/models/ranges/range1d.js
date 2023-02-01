var _a;
import { Range } from "./range";
export class Range1d extends Range {
    constructor(attrs) {
        super(attrs);
    }
    _set_auto_bounds() {
        if (this.bounds == "auto") {
            const min = Math.min(this._reset_start, this._reset_end);
            const max = Math.max(this._reset_start, this._reset_end);
            this.setv({ bounds: [min, max] }, { silent: true });
        }
    }
    initialize() {
        super.initialize();
        this._set_auto_bounds();
    }
    get min() {
        return Math.min(this.start, this.end);
    }
    get max() {
        return Math.max(this.start, this.end);
    }
    reset() {
        this._set_auto_bounds();
        const { _reset_start, _reset_end } = this;
        if (this.start != _reset_start || this.end != _reset_end)
            this.setv({ start: _reset_start, end: _reset_end });
        else
            this.change.emit();
    }
    map(fn) {
        return new Range1d({ start: fn(this.start), end: fn(this.end) });
    }
    widen(v) {
        let { start, end } = this;
        if (this.is_reversed) {
            start += v;
            end -= v;
        }
        else {
            start -= v;
            end += v;
        }
        return new Range1d({ start, end });
    }
}
_a = Range1d;
Range1d.__name__ = "Range1d";
(() => {
    _a.define(({ Number, Nullable }) => ({
        start: [Number, 0],
        end: [Number, 1],
        reset_start: [Nullable(Number), null, {
                on_update(reset_start, self) {
                    self._reset_start = reset_start ?? self.start;
                },
            }],
        reset_end: [Nullable(Number), null, {
                on_update(reset_end, self) {
                    self._reset_end = reset_end ?? self.end;
                },
            }],
    }));
})();
//# sourceMappingURL=range1d.js.map