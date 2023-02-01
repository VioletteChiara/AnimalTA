var _a;
import { ContinuousTicker } from "./continuous_ticker";
export class SingleIntervalTicker extends ContinuousTicker {
    constructor(attrs) {
        super(attrs);
    }
    get_interval(_data_low, _data_high, _n_desired_ticks) {
        return this.interval;
    }
    get_min_interval() {
        return this.interval;
    }
    get_max_interval() {
        return this.interval;
    }
}
_a = SingleIntervalTicker;
SingleIntervalTicker.__name__ = "SingleIntervalTicker";
(() => {
    _a.define(({ Number }) => ({
        interval: [Number],
    }));
})();
//# sourceMappingURL=single_interval_ticker.js.map