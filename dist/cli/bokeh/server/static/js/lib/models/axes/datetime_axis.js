var _a;
import { LinearAxis, LinearAxisView } from "./linear_axis";
import { DatetimeTickFormatter } from "../formatters/datetime_tick_formatter";
import { DatetimeTicker } from "../tickers/datetime_ticker";
export class DatetimeAxisView extends LinearAxisView {
}
DatetimeAxisView.__name__ = "DatetimeAxisView";
export class DatetimeAxis extends LinearAxis {
    constructor(attrs) {
        super(attrs);
    }
}
_a = DatetimeAxis;
DatetimeAxis.__name__ = "DatetimeAxis";
(() => {
    _a.prototype.default_view = DatetimeAxisView;
    _a.override({
        ticker: () => new DatetimeTicker(),
        formatter: () => new DatetimeTickFormatter(),
    });
})();
//# sourceMappingURL=datetime_axis.js.map