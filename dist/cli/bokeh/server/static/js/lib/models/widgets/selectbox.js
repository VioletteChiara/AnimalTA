var _a;
import { select, option, optgroup, empty, append } from "../../core/dom";
import { isString, isArray } from "../../core/util/types";
import { entries } from "../../core/util/object";
import { InputWidget, InputWidgetView } from "./input_widget";
import * as inputs from "../../styles/widgets/inputs.css";
export class SelectView extends InputWidgetView {
    constructor() {
        super(...arguments);
        this._known_values = new Set();
    }
    connect_signals() {
        super.connect_signals();
        const { value, options } = this.model.properties;
        this.on_change(value, () => {
            this._update_value();
        });
        this.on_change(options, () => {
            empty(this.input_el);
            append(this.input_el, ...this.options_el());
            this._update_value();
        });
    }
    options_el() {
        const { _known_values } = this;
        _known_values.clear();
        function build_options(values) {
            return values.map((el) => {
                let value, label;
                if (isString(el))
                    value = label = el;
                else
                    [value, label] = el;
                _known_values.add(value);
                return option({ value }, label);
            });
        }
        const { options } = this.model;
        if (isArray(options))
            return build_options(options);
        else
            return entries(options).map(([label, values]) => optgroup({ label }, build_options(values)));
    }
    render() {
        super.render();
        this.input_el = select({
            class: inputs.input,
            name: this.model.name,
            disabled: this.model.disabled,
        }, this.options_el());
        this._update_value();
        this.input_el.addEventListener("change", () => this.change_input());
        this.group_el.appendChild(this.input_el);
    }
    change_input() {
        const value = this.input_el.value;
        this.model.value = value;
        super.change_input();
    }
    _update_value() {
        const { value } = this.model;
        if (this._known_values.has(value))
            this.input_el.value = value;
        else
            this.input_el.removeAttribute("value");
    }
}
SelectView.__name__ = "SelectView";
export class Select extends InputWidget {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Select;
Select.__name__ = "Select";
(() => {
    _a.prototype.default_view = SelectView;
    _a.define(({ String, Array, Tuple, Dict, Or }) => {
        const Options = Array(Or(String, Tuple(String, String)));
        return {
            value: [String, ""],
            options: [Or(Options, Dict(Options)), []],
        };
    });
})();
//# sourceMappingURL=selectbox.js.map