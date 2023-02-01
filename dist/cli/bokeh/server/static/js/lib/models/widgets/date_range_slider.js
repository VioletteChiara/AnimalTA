var _a;
import tz from "timezone";
import { AbstractSlider, AbstractRangeSliderView } from "./abstract_slider";
import { isString } from "../../core/util/types";
export class DateRangeSliderView extends AbstractRangeSliderView {
}
DateRangeSliderView.__name__ = "DateRangeSliderView";
export class DateRangeSlider extends AbstractSlider {
    constructor(attrs) {
        super(attrs);
        this.behaviour = "drag";
        this.connected = [false, true, false];
    }
    _formatter(value, format) {
        if (isString(format))
            return tz(value, format);
        else
            return format.compute(value);
    }
}
_a = DateRangeSlider;
DateRangeSlider.__name__ = "DateRangeSlider";
(() => {
    _a.prototype.default_view = DateRangeSliderView;
    _a.override({
        format: "%d %b %Y",
    });
})();
//# sourceMappingURL=date_range_slider.js.map