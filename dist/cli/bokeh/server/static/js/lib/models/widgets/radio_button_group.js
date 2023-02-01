var _a;
import { ButtonGroup, ButtonGroupView } from "./button_group";
import { classes } from "../../core/dom";
import * as buttons from "../../styles/buttons.css";
export class RadioButtonGroupView extends ButtonGroupView {
    change_active(i) {
        if (this.model.active !== i) {
            this.model.active = i;
        }
    }
    _update_active() {
        const { active } = this.model;
        this._buttons.forEach((button, i) => {
            classes(button).toggle(buttons.active, active === i);
        });
    }
}
RadioButtonGroupView.__name__ = "RadioButtonGroupView";
export class RadioButtonGroup extends ButtonGroup {
    constructor(attrs) {
        super(attrs);
    }
}
_a = RadioButtonGroup;
RadioButtonGroup.__name__ = "RadioButtonGroup";
(() => {
    _a.prototype.default_view = RadioButtonGroupView;
    _a.define(({ Int, Nullable }) => ({
        active: [Nullable(Int), null],
    }));
})();
//# sourceMappingURL=radio_button_group.js.map