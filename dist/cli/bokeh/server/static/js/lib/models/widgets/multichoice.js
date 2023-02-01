var _a;
import Choices from "choices.js";
import { select } from "../../core/dom";
import { isString } from "../../core/util/types";
import { CachedVariadicBox } from "../../core/layout/html";
import * as inputs from "../../styles/widgets/inputs.css";
import choices_css from "../../styles/widgets/choices.css";
import { InputWidget, InputWidgetView } from "./input_widget";
export class MultiChoiceView extends InputWidgetView {
    constructor() {
        super(...arguments);
        this._last_height = null;
    }
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.properties.disabled.change, () => this.set_disabled());
        const { value, max_items, option_limit, search_option_limit, delete_button, placeholder, options, name, title } = this.model.properties;
        this.on_change([value, max_items, option_limit, search_option_limit, delete_button, placeholder, options, name, title], () => this.render());
    }
    styles() {
        return [...super.styles(), choices_css];
    }
    _update_layout() {
        this.layout = new CachedVariadicBox(this.el);
        this.layout.set_sizing(this.box_sizing());
    }
    render() {
        super.render();
        this.input_el = select({
            multiple: true,
            class: inputs.input,
            name: this.model.name,
            disabled: this.model.disabled,
        });
        this.group_el.appendChild(this.input_el);
        const selected = new Set(this.model.value);
        const choices = this.model.options.map((opt) => {
            let value, label;
            if (isString(opt))
                value = label = opt;
            else
                [value, label] = opt;
            return { value, label, selected: selected.has(value) };
        });
        const fill = this.model.solid ? "solid" : "light";
        const item = `choices__item ${fill}`;
        const button = `choices__button ${fill}`;
        const options = {
            choices,
            duplicateItemsAllowed: false,
            removeItemButton: this.model.delete_button,
            classNames: { item, button }, // XXX: bad typings, missing Partial<>
        };
        if (this.model.placeholder != null)
            options.placeholderValue = this.model.placeholder;
        if (this.model.max_items != null)
            options.maxItemCount = this.model.max_items;
        if (this.model.option_limit != null)
            options.renderChoiceLimit = this.model.option_limit;
        if (this.model.search_option_limit != null)
            options.searchResultLimit = this.model.search_option_limit;
        this.choice_el = new Choices(this.input_el, options);
        const height = () => this.choice_el.containerOuter.element.getBoundingClientRect().height;
        if (this._last_height != null && this._last_height != height()) {
            this.root.invalidate_layout();
        }
        this._last_height = height();
        this.input_el.addEventListener("change", () => this.change_input());
    }
    set_disabled() {
        if (this.model.disabled)
            this.choice_el.disable();
        else
            this.choice_el.enable();
    }
    change_input() {
        const is_focused = this.el.querySelector("select:focus") != null;
        const values = [];
        for (const el of this.el.querySelectorAll("option")) {
            if (el.selected)
                values.push(el.value);
        }
        this.model.value = values;
        super.change_input();
        // Restore focus back to the <select> afterwards,
        // so that even if python on_change callback is invoked,
        // focus remains on <select> and one can seamlessly scroll
        // up/down.
        if (is_focused)
            this.input_el.focus();
    }
}
MultiChoiceView.__name__ = "MultiChoiceView";
export class MultiChoice extends InputWidget {
    constructor(attrs) {
        super(attrs);
    }
}
_a = MultiChoice;
MultiChoice.__name__ = "MultiChoice";
(() => {
    _a.prototype.default_view = MultiChoiceView;
    _a.define(({ Boolean, Int, String, Array, Tuple, Or, Nullable }) => ({
        value: [Array(String), []],
        options: [Array(Or(String, Tuple(String, String))), []],
        max_items: [Nullable(Int), null],
        delete_button: [Boolean, true],
        placeholder: [Nullable(String), null],
        option_limit: [Nullable(Int), null],
        search_option_limit: [Nullable(Int), null],
        solid: [Boolean, true],
    }));
})();
//# sourceMappingURL=multichoice.js.map