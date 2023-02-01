var _a;
import { TextLikeInput, TextLikeInputView } from "./text_like_input";
import { textarea } from "../../core/dom";
import * as inputs from "../../styles/widgets/inputs.css";
export class TextAreaInputView extends TextLikeInputView {
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.properties.rows.change, () => this.input_el.rows = this.model.rows);
        this.connect(this.model.properties.cols.change, () => this.input_el.cols = this.model.cols);
    }
    _render_input() {
        this.input_el = textarea({ class: inputs.input });
    }
    render() {
        super.render();
        this.input_el.cols = this.model.cols;
        this.input_el.rows = this.model.rows;
    }
}
TextAreaInputView.__name__ = "TextAreaInputView";
export class TextAreaInput extends TextLikeInput {
    constructor(attrs) {
        super(attrs);
    }
}
_a = TextAreaInput;
TextAreaInput.__name__ = "TextAreaInput";
(() => {
    _a.prototype.default_view = TextAreaInputView;
    _a.define(({ Int }) => ({
        cols: [Int, 20],
        rows: [Int, 2],
    }));
    _a.override({
        max_length: 500,
    });
})();
//# sourceMappingURL=textarea_input.js.map