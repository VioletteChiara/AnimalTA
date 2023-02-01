var _a;
import * as Numbro from "@bokeh/numbro";
import { TickFormatter } from "./tick_formatter";
import { RoundingFunction } from "../../core/enums";
export class NumeralTickFormatter extends TickFormatter {
    constructor(attrs) {
        super(attrs);
    }
    get _rounding_fn() {
        switch (this.rounding) {
            case "round":
            case "nearest":
                return Math.round;
            case "floor":
            case "rounddown":
                return Math.floor;
            case "ceil":
            case "roundup":
                return Math.ceil;
        }
    }
    doFormat(ticks, _opts) {
        const { format, language, _rounding_fn } = this;
        return ticks.map((tick) => Numbro.format(tick, format, language, _rounding_fn));
    }
}
_a = NumeralTickFormatter;
NumeralTickFormatter.__name__ = "NumeralTickFormatter";
(() => {
    _a.define(({ String }) => ({
        // TODO (bev) all of these could be tightened up
        format: [String, "0,0"],
        language: [String, "en"],
        rounding: [RoundingFunction, "round"],
    }));
})();
//# sourceMappingURL=numeral_tick_formatter.js.map