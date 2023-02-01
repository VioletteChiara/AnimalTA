var _a;
import { ContinuousTicker } from "./continuous_ticker";
import { argmin, nth } from "../../core/util/array";
import { clamp, log } from "../../core/util/math";
export class AdaptiveTicker extends ContinuousTicker {
    constructor(attrs) {
        super(attrs);
    }
    get_min_interval() {
        return this.min_interval;
    }
    get_max_interval() {
        return this.max_interval ?? Infinity;
    }
    // These arguments control the range of possible intervals.  The interval I
    // returned by get_interval() will be the one that most closely matches the
    // desired number of ticks, subject to the following constraints:
    // I = (M * B^N), where
    // M is a member of mantissas,
    // B is base,
    // and N is an integer;
    // and min_interval <= I <= max_interval.
    initialize() {
        super.initialize();
        const prefix_mantissa = nth(this.mantissas, -1) / this.base;
        const suffix_mantissa = nth(this.mantissas, 0) * this.base;
        this.extended_mantissas = [prefix_mantissa, ...this.mantissas, suffix_mantissa];
        this.base_factor = this.get_min_interval() === 0.0 ? 1.0 : this.get_min_interval();
    }
    get_interval(data_low, data_high, desired_n_ticks) {
        const data_range = data_high - data_low;
        const ideal_interval = this.get_ideal_interval(data_low, data_high, desired_n_ticks);
        const interval_exponent = Math.floor(log(ideal_interval / this.base_factor, this.base));
        const ideal_magnitude = this.base ** interval_exponent * this.base_factor;
        // An untested optimization.
        //   const ideal_mantissa = ideal_interval / ideal_magnitude
        //   index = sorted_index(this.extended_mantissas, ideal_mantissa)
        //   candidate_mantissas = this.extended_mantissas[index..index + 1]
        const candidate_mantissas = this.extended_mantissas;
        const errors = candidate_mantissas.map((mantissa) => {
            return Math.abs(desired_n_ticks - (data_range / (mantissa * ideal_magnitude)));
        });
        const best_mantissa = candidate_mantissas[argmin(errors)];
        const interval = best_mantissa * ideal_magnitude;
        return clamp(interval, this.get_min_interval(), this.get_max_interval());
    }
}
_a = AdaptiveTicker;
AdaptiveTicker.__name__ = "AdaptiveTicker";
(() => {
    _a.define(({ Number, Array, Nullable }) => ({
        base: [Number, 10.0],
        mantissas: [Array(Number), [1, 2, 5]],
        min_interval: [Number, 0.0],
        max_interval: [Nullable(Number), null],
    }));
})();
//# sourceMappingURL=adaptive_ticker.js.map