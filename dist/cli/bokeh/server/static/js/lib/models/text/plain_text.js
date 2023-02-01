var _a;
import { BaseText, BaseTextView } from "./base_text";
import { TextBox } from "../../core/graphics";
export class PlainTextView extends BaseTextView {
    initialize() {
        super.initialize();
        this._has_finished = true;
    }
    graphics() {
        return new TextBox({ text: this.model.text });
    }
}
PlainTextView.__name__ = "PlainTextView";
export class PlainText extends BaseText {
    constructor(attrs) {
        super(attrs);
    }
}
_a = PlainText;
PlainText.__name__ = "PlainText";
(() => {
    _a.prototype.default_view = PlainTextView;
})();
//# sourceMappingURL=plain_text.js.map