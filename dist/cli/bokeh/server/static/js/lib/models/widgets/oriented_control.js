var _a;
import { Control, ControlView } from "./control";
import { Orientation } from "../../core/enums";
export class OrientedControlView extends ControlView {
    get orientation() {
        return this.model.orientation;
    }
}
OrientedControlView.__name__ = "OrientedControlView";
export class OrientedControl extends Control {
    constructor(attrs) {
        super(attrs);
    }
}
_a = OrientedControl;
OrientedControl.__name__ = "OrientedControl";
(() => {
    _a.define(() => ({
        orientation: [Orientation, "horizontal"],
    }));
})();
//# sourceMappingURL=oriented_control.js.map