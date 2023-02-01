import { View } from "./view";
import { createElement, remove } from "./dom";
export class DOMView extends View {
    initialize() {
        super.initialize();
        this.el = this._createElement();
    }
    remove() {
        remove(this.el);
        super.remove();
    }
    css_classes() {
        return [];
    }
    render() { }
    renderTo(element) {
        element.appendChild(this.el);
        this.render();
        this._has_finished = true;
        this.notify_finished();
    }
    _createElement() {
        return createElement(this.constructor.tag_name, { class: this.css_classes() });
    }
}
DOMView.__name__ = "DOMView";
DOMView.tag_name = "div";
//# sourceMappingURL=dom_view.js.map