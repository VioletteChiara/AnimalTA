var _a;
import tz from "timezone";
import { AbstractSlider, AbstractSliderView } from "./abstract_slider";
import { isString } from "../../core/util/types";
export class DateSliderView extends AbstractSliderView {
}
DateSliderView.__name__ = "DateSliderView";
export class DateSlider extends AbstractSlider {
    constructor(attrs) {
        super(attrs);
        this.behaviour = "tap";
        this.connected = [true, false];
    }
    _formatter(value, format) {
        if (isString(format))
            return tz(value, format);
        else
            return format.compute(value);
    }
}
_a = DateSlider;
DateSlider.__name__ = "DateSlider";
(() => {
    _a.prototype.default_view = DateSliderView;
    _a.override({
        format: "%d %b %Y",
    });
})();
//# sourceMappingURL=date_slider.js.map