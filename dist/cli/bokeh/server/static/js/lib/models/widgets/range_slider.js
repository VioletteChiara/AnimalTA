var _a;
import * as numbro from "@bokeh/numbro";
import { AbstractSlider, AbstractRangeSliderView } from "./abstract_slider";
import { isString } from "../../core/util/types";
export class RangeSliderView extends AbstractRangeSliderView {
}
RangeSliderView.__name__ = "RangeSliderView";
export class RangeSlider extends AbstractSlider {
    constructor(attrs) {
        super(attrs);
        this.behaviour = "drag";
        this.connected = [false, true, false];
    }
    _formatter(value, format) {
        if (isString(format))
            return numbro.format(value, format);
        else
            return format.compute(value);
    }
}
_a = RangeSlider;
RangeSlider.__name__ = "RangeSlider";
(() => {
    _a.prototype.default_view = RangeSliderView;
    _a.override({
        format: "0[.]00",
    });
})();
//# sourceMappingURL=range_slider.js.map