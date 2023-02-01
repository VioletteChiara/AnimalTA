import { div, classes, display, undisplay, empty, remove, Keys } from "../dom";
import { reversed } from "./array";
import /*menus_css,*/ * as menus from "../../styles/menus.css";
export class ContextMenu {
    constructor(items, options = {}) {
        this.items = items;
        this.el = div();
        this._open = false;
        this._item_click = (entry) => {
            entry.handler?.();
            this.hide();
        };
        this._on_mousedown = (event) => {
            const { target } = event;
            if (target instanceof Node && this.el.contains(target))
                return;
            if (this.prevent_hide?.(event))
                return;
            this.hide();
        };
        this._on_keydown = (event) => {
            if (event.keyCode == Keys.Esc)
                this.hide();
        };
        this._on_blur = () => {
            this.hide();
        };
        this.orientation = options.orientation ?? "vertical";
        this.reversed = options.reversed ?? false;
        this.prevent_hide = options.prevent_hide;
        undisplay(this.el);
    }
    get is_open() {
        return this._open;
    }
    get can_open() {
        return this.items.length != 0;
    }
    remove() {
        remove(this.el);
        this._unlisten();
    }
    _listen() {
        document.addEventListener("mousedown", this._on_mousedown);
        document.addEventListener("keydown", this._on_keydown);
        window.addEventListener("blur", this._on_blur);
    }
    _unlisten() {
        document.removeEventListener("mousedown", this._on_mousedown);
        document.removeEventListener("keydown", this._on_keydown);
        window.removeEventListener("blur", this._on_blur);
    }
    _position(at) {
        const parent_el = this.el.parentElement;
        if (parent_el != null) {
            const pos = (() => {
                if ("left_of" in at) {
                    const { left, top } = at.left_of.getBoundingClientRect();
                    return { right: left, top };
                }
                if ("right_of" in at) {
                    const { top, right } = at.right_of.getBoundingClientRect();
                    return { left: right, top };
                }
                if ("below" in at) {
                    const { left, bottom } = at.below.getBoundingClientRect();
                    return { left, top: bottom };
                }
                if ("above" in at) {
                    const { left, top } = at.above.getBoundingClientRect();
                    return { left, bottom: top };
                }
                return at;
            })();
            const parent = parent_el.getBoundingClientRect();
            this.el.style.left = pos.left != null ? `${pos.left - parent.left}px` : "";
            this.el.style.top = pos.top != null ? `${pos.top - parent.top}px` : "";
            this.el.style.right = pos.right != null ? `${parent.right - pos.right}px` : "";
            this.el.style.bottom = pos.bottom != null ? `${parent.bottom - pos.bottom}px` : "";
        }
    }
    /*
    override styles(): string[] {
      return [...super.styles(), menus_css]
    }
    */
    render() {
        empty(this.el, true);
        classes(this.el).add("bk-context-menu", `bk-${this.orientation}`);
        const items = this.reversed ? reversed(this.items) : this.items;
        for (const item of items) {
            let el;
            if (item == null) {
                el = div({ class: menus.divider });
            }
            else if (item.if != null && !item.if()) {
                continue;
            }
            else if (item.content != null) {
                el = item.content;
            }
            else {
                const icon = item.icon != null ? div({ class: ["bk-menu-icon", item.icon] }) : null;
                const classes = [item.active?.() ? "bk-active" : null, item.class];
                el = div({ class: classes, title: item.tooltip, tabIndex: 0 }, icon, item.label, item.content);
                el.addEventListener("click", () => {
                    this._item_click(item);
                });
                el.addEventListener("keydown", (event) => {
                    if (event.keyCode == Keys.Enter) {
                        this._item_click(item);
                    }
                });
            }
            this.el.appendChild(el);
        }
    }
    show(at) {
        if (this.items.length == 0)
            return;
        if (!this._open) {
            this.render();
            if (this.el.children.length == 0)
                return;
            this._position(at ?? { left: 0, top: 0 });
            display(this.el);
            this._listen();
            this._open = true;
        }
    }
    hide() {
        if (this._open) {
            this._open = false;
            this._unlisten();
            undisplay(this.el);
        }
    }
    toggle(at) {
        this._open ? this.hide() : this.show(at);
    }
}
ContextMenu.__name__ = "ContextMenu";
//# sourceMappingURL=menus.js.map