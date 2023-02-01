var _a;
import { TickFormatter } from "./tick_formatter";
import { sprintf } from "../../core/util/templating";
export class PrintfTickFormatter extends TickFormatter {
    constructor(attrs) {
        super(attrs);
    }
    doFormat(ticks, _opts) {
        return ticks.map((tick) => sprintf(this.format, tick));
    }
}
_a = PrintfTickFormatter;
PrintfTickFormatter.__name__ = "PrintfTickFormatter";
(() => {
    _a.define(({ String }) => ({
        format: [String, "%s"],
    }));
})();
//# sourceMappingURL=printf_tick_formatter.js.map