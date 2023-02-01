var _a;
import { TextInput, TextInputView } from "./text_input";
import { empty, display, undisplay, div, Keys } from "../../core/dom";
import { clamp } from "../../core/util/math";
import menus_css, * as menus from "../../styles/menus.css";
export class AutocompleteInputView extends TextInputView {
    constructor() {
        super(...arguments);
        this._open = false;
        this._last_value = "";
        this._hover_index = 0;
    }
    styles() {
        return [...super.styles(), menus_css];
    }
    render() {
        super.render();
        this.input_el.addEventListener("keydown", (event) => this._keydown(event));
        this.input_el.addEventListener("keyup", (event) => this._keyup(event));
        this.menu = div({ class: [menus.menu, menus.below] });
        this.menu.addEventListener("click", (event) => this._menu_click(event));
        this.menu.addEventListener("mouseover", (event) => this._menu_hover(event));
        this.el.appendChild(this.menu);
        undisplay(this.menu);
    }
    change_input() {
        if (this._open && this.menu.children.length > 0) {
            this.model.value = this.menu.children[this._hover_index].textContent;
            this.input_el.focus();
            this._hide_menu();
        }
        else if (!this.model.restrict) {
            super.change_input();
        }
    }
    _update_completions(completions) {
        empty(this.menu);
        for (const text of completions) {
            const item = div(text);
            this.menu.appendChild(item);
        }
        if (completions.length > 0)
            this.menu.children[0].classList.add(menus.active);
    }
    _show_menu() {
        if (!this._open) {
            this._open = true;
            this._hover_index = 0;
            this._last_value = this.model.value;
            display(this.menu);
            const listener = (event) => {
                const { target } = event;
                if (target instanceof HTMLElement && !this.el.contains(target)) {
                    document.removeEventListener("click", listener);
                    this._hide_menu();
                }
            };
            document.addEventListener("click", listener);
        }
    }
    _hide_menu() {
        if (this._open) {
            this._open = false;
            undisplay(this.menu);
        }
    }
    _menu_click(event) {
        if (event.target != event.currentTarget && event.target instanceof Element) {
            this.model.value = event.target.textContent;
            this.input_el.focus();
            this._hide_menu();
        }
    }
    _menu_hover(event) {
        if (event.target != event.currentTarget && event.target instanceof Element) {
            let i = 0;
            for (i = 0; i < this.menu.children.length; i++) {
                if (this.menu.children[i].textContent == event.target.textContent)
                    break;
            }
            this._bump_hover(i);
        }
    }
    _bump_hover(new_index) {
        const n_children = this.menu.children.length;
        if (this._open && n_children > 0) {
            this.menu.children[this._hover_index].classList.remove(menus.active);
            this._hover_index = clamp(new_index, 0, n_children - 1);
            this.menu.children[this._hover_index].classList.add(menus.active);
        }
    }
    _keydown(_event) { }
    _keyup(event) {
        switch (event.keyCode) {
            case Keys.Enter: {
                this.change_input();
                break;
            }
            case Keys.Esc: {
                this._hide_menu();
                break;
            }
            case Keys.Up: {
                this._bump_hover(this._hover_index - 1);
                break;
            }
            case Keys.Down: {
                this._bump_hover(this._hover_index + 1);
                break;
            }
            default: {
                const value = this.input_el.value;
                if (value.length < this.model.min_characters) {
                    this._hide_menu();
                    return;
                }
                const completions = [];
                const { case_sensitive } = this.model;
                let acnorm;
                if (case_sensitive) {
                    acnorm = (t) => t;
                }
                else {
                    acnorm = (t) => t.toLowerCase();
                }
                for (const text of this.model.completions) {
                    if (acnorm(text).startsWith(acnorm(value))) {
                        completions.push(text);
                    }
                }
                this._update_completions(completions);
                if (completions.length == 0)
                    this._hide_menu();
                else
                    this._show_menu();
            }
        }
    }
}
AutocompleteInputView.__name__ = "AutocompleteInputView";
export class AutocompleteInput extends TextInput {
    constructor(attrs) {
        super(attrs);
    }
}
_a = AutocompleteInput;
AutocompleteInput.__name__ = "AutocompleteInput";
(() => {
    _a.prototype.default_view = AutocompleteInputView;
    _a.define(({ Boolean, Int, String, Array }) => ({
        completions: [Array(String), []],
        min_characters: [Int, 2],
        case_sensitive: [Boolean, true],
        restrict: [Boolean, true],
    }));
})();
//# sourceMappingURL=autocomplete_input.js.map