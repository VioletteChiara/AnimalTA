var _a;
import { AxisView } from "./axis";
import { LinearAxis } from "./linear_axis";
import { MercatorTickFormatter } from "../formatters/mercator_tick_formatter";
import { MercatorTicker } from "../tickers/mercator_ticker";
export class MercatorAxisView extends AxisView {
}
MercatorAxisView.__name__ = "MercatorAxisView";
export class MercatorAxis extends LinearAxis {
    constructor(attrs) {
        super(attrs);
    }
}
_a = MercatorAxis;
MercatorAxis.__name__ = "MercatorAxis";
(() => {
    _a.prototype.default_view = MercatorAxisView;
    _a.override({
        ticker: () => new MercatorTicker({ dimension: "lat" }),
        formatter: () => new MercatorTickFormatter({ dimension: "lat" }),
    });
})();
//# sourceMappingURL=mercator_axis.js.map