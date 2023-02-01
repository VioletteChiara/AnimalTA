var _a;
import { Control, ControlView } from "./control";
import { div, label } from "../../core/dom";
import inputs_css, * as inputs from "../../styles/widgets/inputs.css";
export class InputWidgetView extends ControlView {
    *controls() {
        yield this.input_el;
    }
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.properties.title.change, () => {
            this.label_el.textContent = this.model.title;
        });
    }
    styles() {
        return [...super.styles(), inputs_css];
    }
    render() {
        super.render();
        const { title } = this.model;
        this.label_el = label({ style: { display: title.length == 0 ? "none" : "" } }, title);
        this.group_el = div({ class: inputs.input_group }, this.label_el);
        this.el.appendChild(this.group_el);
    }
    change_input() { }
}
InputWidgetView.__name__ = "InputWidgetView";
export class InputWidget extends Control {
    constructor(attrs) {
        super(attrs);
    }
}
_a = InputWidget;
InputWidget.__name__ = "InputWidget";
(() => {
    _a.define(({ String }) => ({
        title: [String, ""],
    }));
})();
//# sourceMappingURL=input_widget.js.map