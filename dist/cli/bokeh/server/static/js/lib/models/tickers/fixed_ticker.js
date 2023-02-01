var _a;
import { ContinuousTicker } from "./continuous_ticker";
export class FixedTicker extends ContinuousTicker {
    constructor(attrs) {
        super(attrs);
    }
    get_ticks_no_defaults(_data_low, _data_high, _cross_loc, _desired_n_ticks) {
        return {
            major: this.ticks,
            minor: this.minor_ticks,
        };
    }
    // XXX: whatever, because FixedTicker needs to fulfill the interface somehow
    get_interval(_data_low, _data_high, _desired_n_ticks) {
        return 0;
    }
    get_min_interval() {
        return 0;
    }
    get_max_interval() {
        return 0;
    }
}
_a = FixedTicker;
FixedTicker.__name__ = "FixedTicker";
(() => {
    _a.define(({ Number, Array }) => ({
        ticks: [Array(Number), []],
        minor_ticks: [Array(Number), []],
    }));
})();
//# sourceMappingURL=fixed_ticker.js.map