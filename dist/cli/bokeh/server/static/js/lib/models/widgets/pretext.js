var _a;
import { Markup, MarkupView } from "./markup";
import { pre } from "../../core/dom";
export class PreTextView extends MarkupView {
    render() {
        super.render();
        const content = pre({ style: { overflow: "auto" } }, this.model.text);
        this.markup_el.appendChild(content);
    }
}
PreTextView.__name__ = "PreTextView";
export class PreText extends Markup {
    constructor(attrs) {
        super(attrs);
    }
}
_a = PreText;
PreText.__name__ = "PreText";
(() => {
    _a.prototype.default_view = PreTextView;
})();
//# sourceMappingURL=pretext.js.map