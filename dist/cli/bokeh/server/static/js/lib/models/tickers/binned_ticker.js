var _a;
import { Ticker } from "./ticker";
import { ScanningColorMapper } from "../mappers/scanning_color_mapper";
import { left_edge_index } from "../../core/util/arrayable";
export class BinnedTicker extends Ticker {
    constructor(attrs) {
        super(attrs);
    }
    get_ticks(data_low, data_high, _range, _cross_loc) {
        const { binning } = this.mapper.metrics;
        const k_low = Math.max(0, left_edge_index(data_low, binning));
        const k_high = Math.min(left_edge_index(data_high, binning) + 1, binning.length - 1);
        const _major = [];
        for (let k = k_low; k <= k_high; k++) {
            _major.push(binning[k]);
        }
        const { num_major_ticks } = this;
        const major = [];
        const n = num_major_ticks == "auto" ? _major.length : num_major_ticks;
        const step = Math.max(1, Math.floor(_major.length / n));
        for (let i = 0; i < _major.length; i += step) {
            major.push(_major[i]);
        }
        return {
            major,
            minor: [],
        };
    }
}
_a = BinnedTicker;
BinnedTicker.__name__ = "BinnedTicker";
(() => {
    _a.define(({ Number, Ref, Or, Auto }) => ({
        mapper: [Ref(ScanningColorMapper)],
        num_major_ticks: [Or(Number, Auto), 8],
    }));
})();
//# sourceMappingURL=binned_ticker.js.map