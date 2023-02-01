var _a;
import { Markup, MarkupView } from "./markup";
import { p as paragraph } from "../../core/dom";
export class ParagraphView extends MarkupView {
    render() {
        super.render();
        // This overrides default user-agent styling and helps layout work
        const content = paragraph({ style: { margin: 0 } });
        if (this.has_math_disabled())
            content.textContent = this.model.text;
        else
            content.innerHTML = this.process_tex();
        this.markup_el.appendChild(content);
    }
}
ParagraphView.__name__ = "ParagraphView";
export class Paragraph extends Markup {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Paragraph;
Paragraph.__name__ = "Paragraph";
(() => {
    _a.prototype.default_view = ParagraphView;
})();
//# sourceMappingURL=paragraph.js.map