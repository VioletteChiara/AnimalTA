var _a;
import { AbstractButton, AbstractButtonView } from "./abstract_button";
import { classes } from "../../core/dom";
import * as inputs from "../../styles/buttons.css";
export class ToggleView extends AbstractButtonView {
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.properties.active.change, () => this._update_active());
    }
    render() {
        super.render();
        this._update_active();
    }
    click() {
        this.model.active = !this.model.active;
        super.click();
    }
    _update_active() {
        classes(this.button_el).toggle(inputs.active, this.model.active);
    }
}
ToggleView.__name__ = "ToggleView";
export class Toggle extends AbstractButton {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Toggle;
Toggle.__name__ = "Toggle";
(() => {
    _a.prototype.default_view = ToggleView;
    _a.define(({ Boolean }) => ({
        active: [Boolean, false],
    }));
    _a.override({
        label: "Toggle",
    });
})();
//# sourceMappingURL=toggle.js.map