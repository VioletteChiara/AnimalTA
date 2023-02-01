var _a;
import { ContinuousAxis, ContinuousAxisView } from "./continuous_axis";
import { BasicTickFormatter } from "../formatters/basic_tick_formatter";
import { BasicTicker } from "../tickers/basic_ticker";
export class LinearAxisView extends ContinuousAxisView {
}
LinearAxisView.__name__ = "LinearAxisView";
export class LinearAxis extends ContinuousAxis {
    constructor(attrs) {
        super(attrs);
    }
}
_a = LinearAxis;
LinearAxis.__name__ = "LinearAxis";
(() => {
    _a.prototype.default_view = LinearAxisView;
    _a.override({
        ticker: () => new BasicTicker(),
        formatter: () => new BasicTickFormatter(),
    });
})();
//# sourceMappingURL=linear_axis.js.map