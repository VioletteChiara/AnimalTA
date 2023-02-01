import { ContinuousTicker } from "./continuous_ticker";
import * as p from "../../core/properties";
export declare namespace SingleIntervalTicker {
    type Attrs = p.AttrsOf<Props>;
    type Props = ContinuousTicker.Props & {
        interval: p.Property<number>;
    };
}
export interface SingleIntervalTicker extends SingleIntervalTicker.Attrs {
}
export declare class SingleIntervalTicker extends ContinuousTicker {
    properties: SingleIntervalTicker.Props;
    constructor(attrs?: Partial<SingleIntervalTicker.Attrs>);
    get_interval(_data_low: number, _data_high: number, _n_desired_ticks: number): number;
    get_min_interval(): number;
    get_max_interval(): number;
}
//# sourceMappingURL=single_interval_ticker.d.ts.map