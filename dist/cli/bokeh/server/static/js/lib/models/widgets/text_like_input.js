var _a;
import { InputWidget, InputWidgetView } from "./input_widget";
export class TextLikeInputView extends InputWidgetView {
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.properties.name.change, () => this.input_el.name = this.model.name ?? "");
        this.connect(this.model.properties.value.change, () => this.input_el.value = this.model.value);
        this.connect(this.model.properties.value_input.change, () => this.input_el.value = this.model.value_input);
        this.connect(this.model.properties.disabled.change, () => this.input_el.disabled = this.model.disabled);
        this.connect(this.model.properties.placeholder.change, () => this.input_el.placeholder = this.model.placeholder);
        this.connect(this.model.properties.max_length.change, () => {
            const { max_length } = this.model;
            if (max_length != null)
                this.input_el.maxLength = max_length;
            else
                this.input_el.removeAttribute("maxLength");
        });
    }
    render() {
        super.render();
        this._render_input();
        const { input_el } = this;
        input_el.name = this.model.name ?? "";
        input_el.value = this.model.value;
        input_el.disabled = this.model.disabled;
        input_el.placeholder = this.model.placeholder;
        if (this.model.max_length != null)
            input_el.maxLength = this.model.max_length;
        input_el.addEventListener("change", () => this.change_input());
        input_el.addEventListener("input", () => this.change_input_value());
        this.group_el.appendChild(input_el);
    }
    change_input() {
        this.model.value = this.input_el.value;
        super.change_input();
    }
    change_input_value() {
        this.model.value_input = this.input_el.value;
        super.change_input();
    }
}
TextLikeInputView.__name__ = "TextLikeInputView";
export class TextLikeInput extends InputWidget {
    constructor(attrs) {
        super(attrs);
    }
}
_a = TextLikeInput;
TextLikeInput.__name__ = "TextLikeInput";
(() => {
    _a.define(({ Int, String, Nullable }) => ({
        value: [String, ""],
        value_input: [String, ""],
        placeholder: [String, ""],
        max_length: [Nullable(Int), null],
    }));
})();
//# sourceMappingURL=text_like_input.js.map