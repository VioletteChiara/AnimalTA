var _a;
import { Markup, MarkupView } from "./markup";
export class DivView extends MarkupView {
    render() {
        super.render();
        if (this.model.render_as_text)
            this.markup_el.textContent = this.model.text;
        else
            this.markup_el.innerHTML = this.has_math_disabled() ? this.model.text : this.process_tex();
    }
}
DivView.__name__ = "DivView";
export class Div extends Markup {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Div;
Div.__name__ = "Div";
(() => {
    _a.prototype.default_view = DivView;
    _a.define(({ Boolean }) => ({
        render_as_text: [Boolean, false],
    }));
})();
//# sourceMappingURL=div.js.map