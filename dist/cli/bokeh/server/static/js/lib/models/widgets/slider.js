var _a;
import * as numbro from "@bokeh/numbro";
import { AbstractSlider, AbstractSliderView } from "./abstract_slider";
import { isString } from "../../core/util/types";
export class SliderView extends AbstractSliderView {
}
SliderView.__name__ = "SliderView";
export class Slider extends AbstractSlider {
    constructor(attrs) {
        super(attrs);
        this.behaviour = "tap";
        this.connected = [true, false];
    }
    _formatter(value, format) {
        if (isString(format))
            return numbro.format(value, format);
        else
            return format.compute(value);
    }
}
_a = Slider;
Slider.__name__ = "Slider";
(() => {
    _a.prototype.default_view = SliderView;
    _a.override({
        format: "0[.]00",
    });
})();
//# sourceMappingURL=slider.js.map