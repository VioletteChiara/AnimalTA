import { LinearAxis, LinearAxisView } from "./linear_axis";
import { DatetimeTickFormatter } from "../formatters/datetime_tick_formatter";
import { DatetimeTicker } from "../tickers/datetime_ticker";
import * as p from "../../core/properties";
export declare class DatetimeAxisView extends LinearAxisView {
    model: DatetimeAxis;
}
export declare namespace DatetimeAxis {
    type Attrs = p.AttrsOf<Props>;
    type Props = LinearAxis.Props & {
        ticker: p.Property<DatetimeTicker>;
        formatter: p.Property<DatetimeTickFormatter>;
    };
}
export interface DatetimeAxis extends DatetimeAxis.Attrs {
}
export declare class DatetimeAxis extends LinearAxis {
    properties: DatetimeAxis.Props;
    __view_type__: DatetimeAxisView;
    constructor(attrs?: Partial<DatetimeAxis.Attrs>);
    ticker: DatetimeTicker;
    formatter: DatetimeTickFormatter;
}
//# sourceMappingURL=datetime_axis.d.ts.map