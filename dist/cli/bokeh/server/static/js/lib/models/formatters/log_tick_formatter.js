var _a;
import { TickFormatter } from "./tick_formatter";
import { BasicTickFormatter, unicode_replace } from "./basic_tick_formatter";
import { LogTicker } from "../tickers/log_ticker";
import { BaseExpo, TextBox } from "../../core/graphics";
const { abs, log, round } = Math;
export class LogTickFormatter extends TickFormatter {
    constructor(attrs) {
        super(attrs);
    }
    initialize() {
        super.initialize();
        this.basic_formatter = new BasicTickFormatter();
    }
    format_graphics(ticks, opts) {
        if (ticks.length == 0)
            return [];
        const base = this.ticker?.base ?? 10;
        const expos = this._exponents(ticks, base);
        if (expos == null)
            return this.basic_formatter.format_graphics(ticks, opts);
        else {
            return expos.map((expo) => {
                if (abs(expo) < this.min_exponent) {
                    const b = new TextBox({ text: unicode_replace(`${base ** expo}`) });
                    const e = new TextBox({ text: "" });
                    return new BaseExpo(b, e);
                }
                else {
                    const b = new TextBox({ text: unicode_replace(`${base}`) });
                    const e = new TextBox({ text: unicode_replace(`${expo}`) });
                    return new BaseExpo(b, e);
                }
            });
        }
    }
    _exponents(ticks, base) {
        let last_exponent = null;
        const exponents = [];
        for (const tick of ticks) {
            const exponent = round(log(tick) / log(base));
            if (last_exponent != exponent) {
                last_exponent = exponent;
                exponents.push(exponent);
            }
            else
                return null;
        }
        return exponents;
    }
    doFormat(ticks, opts) {
        if (ticks.length == 0)
            return [];
        const base = this.ticker?.base ?? 10;
        const expos = this._exponents(ticks, base);
        if (expos == null)
            return this.basic_formatter.doFormat(ticks, opts);
        else
            return expos.map((expo) => {
                if (abs(expo) < this.min_exponent)
                    return unicode_replace(`${base ** expo}`);
                else
                    return unicode_replace(`${base}^${expo}`);
            });
    }
}
_a = LogTickFormatter;
LogTickFormatter.__name__ = "LogTickFormatter";
(() => {
    _a.define(({ Int, Ref, Nullable }) => ({
        ticker: [Nullable(Ref(LogTicker)), null],
        min_exponent: [Int, 0],
    }));
})();
//# sourceMappingURL=log_tick_formatter.js.map