var _a;
import { ContinuousAxis, ContinuousAxisView } from "./continuous_axis";
import { LogTickFormatter } from "../formatters/log_tick_formatter";
import { LogTicker } from "../tickers/log_ticker";
export class LogAxisView extends ContinuousAxisView {
}
LogAxisView.__name__ = "LogAxisView";
export class LogAxis extends ContinuousAxis {
    constructor(attrs) {
        super(attrs);
    }
}
_a = LogAxis;
LogAxis.__name__ = "LogAxis";
(() => {
    _a.prototype.default_view = LogAxisView;
    _a.override({
        ticker: () => new LogTicker(),
        formatter: () => new LogTickFormatter(),
    });
})();
//# sourceMappingURL=log_axis.js.map