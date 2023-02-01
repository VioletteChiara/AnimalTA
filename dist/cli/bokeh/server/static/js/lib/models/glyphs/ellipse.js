var _a;
import { EllipseOval, EllipseOvalView } from "./ellipse_oval";
export class EllipseView extends EllipseOvalView {
}
EllipseView.__name__ = "EllipseView";
export class Ellipse extends EllipseOval {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Ellipse;
Ellipse.__name__ = "Ellipse";
(() => {
    _a.prototype.default_view = EllipseView;
})();
//# sourceMappingURL=ellipse.js.map