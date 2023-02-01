var _a;
import { TextLikeInput, TextLikeInputView } from "./text_like_input";
import { input } from "../../core/dom";
import * as inputs from "../../styles/widgets/inputs.css";
export class TextInputView extends TextLikeInputView {
    _render_input() {
        this.input_el = input({ type: "text", class: inputs.input });
    }
}
TextInputView.__name__ = "TextInputView";
export class TextInput extends TextLikeInput {
    constructor(attrs) {
        super(attrs);
    }
}
_a = TextInput;
TextInput.__name__ = "TextInput";
(() => {
    _a.prototype.default_view = TextInputView;
})();
//# sourceMappingURL=text_input.js.map