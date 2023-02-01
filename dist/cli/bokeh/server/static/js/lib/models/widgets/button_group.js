var _a;
import { OrientedControl, OrientedControlView } from "./oriented_control";
import { ButtonType } from "../../core/enums";
import { div } from "../../core/dom";
import buttons_css, * as buttons from "../../styles/buttons.css";
export class ButtonGroupView extends OrientedControlView {
    get default_size() {
        return this.orientation == "horizontal" ? this.model.default_size : undefined;
        // TODO: restore this when IE/legacy is dropped
        // return this.orientation == "horizontal" ? super.default_size : undefined
    }
    *controls() {
        yield* this._buttons; // TODO: HTMLButtonElement[]
    }
    connect_signals() {
        super.connect_signals();
        const p = this.model.properties;
        this.on_change(p.button_type, () => this.render());
        this.on_change(p.labels, () => this.render());
        this.on_change(p.active, () => this._update_active());
    }
    styles() {
        return [...super.styles(), buttons_css];
    }
    render() {
        super.render();
        this._buttons = this.model.labels.map((label, i) => {
            const button = div({
                class: [buttons.btn, buttons[`btn_${this.model.button_type}`]],
                disabled: this.model.disabled,
            }, label);
            button.addEventListener("click", () => this.change_active(i));
            return button;
        });
        this._update_active();
        const orient = this.model.orientation == "horizontal" ? buttons.horizontal : buttons.vertical;
        const group = div({ class: [buttons.btn_group, orient] }, this._buttons);
        this.el.appendChild(group);
    }
}
ButtonGroupView.__name__ = "ButtonGroupView";
export class ButtonGroup extends OrientedControl {
    constructor(attrs) {
        super(attrs);
    }
}
_a = ButtonGroup;
ButtonGroup.__name__ = "ButtonGroup";
(() => {
    _a.define(({ String, Array }) => ({
        labels: [Array(String), []],
        button_type: [ButtonType, "default"],
    }));
})();
//# sourceMappingURL=button_group.js.map