var _a;
import { AbstractButton, AbstractButtonView } from "./abstract_button";
import { ButtonClick } from "../../core/bokeh_events";
export class ButtonView extends AbstractButtonView {
    click() {
        this.model.trigger_event(new ButtonClick());
        super.click();
    }
}
ButtonView.__name__ = "ButtonView";
export class Button extends AbstractButton {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Button;
Button.__name__ = "Button";
(() => {
    _a.prototype.default_view = ButtonView;
    _a.override({
        label: "Button",
    });
})();
//# sourceMappingURL=button.js.map