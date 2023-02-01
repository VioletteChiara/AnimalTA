var _a;
import { TickFormatter } from "./tick_formatter";
import { to_fixed } from "../../core/util/string";
export function unicode_replace(input) {
    let output = "";
    for (const c of input) {
        if (c == "-")
            output += "\u2212";
        else
            output += c;
    }
    return output;
}
export class BasicTickFormatter extends TickFormatter {
    constructor(attrs) {
        super(attrs);
        this.last_precision = 3;
    }
    get scientific_limit_low() {
        return 10.0 ** this.power_limit_low;
    }
    get scientific_limit_high() {
        return 10.0 ** this.power_limit_high;
    }
    _need_sci(ticks) {
        if (!this.use_scientific)
            return false;
        const { scientific_limit_high } = this;
        const { scientific_limit_low } = this;
        const zeroish = ticks.length < 2 ? 0 : Math.abs(ticks[1] - ticks[0]) / 10000;
        for (const tick of ticks) {
            const tick_abs = Math.abs(tick);
            if (tick_abs <= zeroish)
                continue;
            if (tick_abs >= scientific_limit_high || tick_abs <= scientific_limit_low) {
                return true;
            }
        }
        return false;
    }
    _format_with_precision(ticks, need_sci, precision) {
        if (need_sci) {
            return ticks.map((tick) => unicode_replace(tick.toExponential(precision)));
        }
        else {
            return ticks.map((tick) => unicode_replace(to_fixed(tick, precision)));
        }
    }
    _auto_precision(ticks, need_sci) {
        const labels = new Array(ticks.length);
        const asc = this.last_precision <= 15;
        outer: for (let x = this.last_precision; asc ? x <= 15 : x >= 1; asc ? x++ : x--) {
            if (need_sci) {
                labels[0] = ticks[0].toExponential(x);
                for (let i = 1; i < ticks.length; i++) {
                    if (labels[i] == labels[i - 1]) {
                        continue outer;
                    }
                }
                this.last_precision = x;
                break;
            }
            else {
                labels[0] = to_fixed(ticks[0], x);
                for (let i = 1; i < ticks.length; i++) {
                    labels[i] = to_fixed(ticks[i], x);
                    if (labels[i] == labels[i - 1]) {
                        continue outer;
                    }
                }
                this.last_precision = x;
                break;
            }
        }
        return this.last_precision;
    }
    doFormat(ticks, _opts) {
        if (ticks.length == 0)
            return [];
        const need_sci = this._need_sci(ticks);
        const precision = this.precision == "auto" ? this._auto_precision(ticks, need_sci) : this.precision;
        return this._format_with_precision(ticks, need_sci, precision);
    }
}
_a = BasicTickFormatter;
BasicTickFormatter.__name__ = "BasicTickFormatter";
(() => {
    _a.define(({ Boolean, Int, Auto, Or }) => ({
        precision: [Or(Int, Auto), "auto"],
        use_scientific: [Boolean, true],
        power_limit_high: [Int, 5],
        power_limit_low: [Int, -3],
    }));
})();
//# sourceMappingURL=basic_tick_formatter.js.map