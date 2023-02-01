var _a;
import { EllipseOval, EllipseOvalView } from "./ellipse_oval";
import { mul } from "../../core/util/arrayable";
export class OvalView extends EllipseOvalView {
    _map_data() {
        super._map_data();
        mul(this.sw, 0.75); // oval drawn from bezier curves = ellipse with width reduced by 3/4
    }
}
OvalView.__name__ = "OvalView";
export class Oval extends EllipseOval {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Oval;
Oval.__name__ = "Oval";
(() => {
    _a.prototype.default_view = OvalView;
})();
//# sourceMappingURL=oval.js.map