var _a;
import { TextInput, TextInputView } from "./text_input";
export class PasswordInputView extends TextInputView {
    render() {
        super.render();
        this.input_el.type = "password";
    }
}
PasswordInputView.__name__ = "PasswordInputView";
export class PasswordInput extends TextInput {
    constructor(attrs) {
        super(attrs);
    }
}
_a = PasswordInput;
PasswordInput.__name__ = "PasswordInput";
(() => {
    _a.prototype.default_view = PasswordInputView;
})();
//# sourceMappingURL=password_input.js.map