var _a;
import { Model } from "../../model";
import { View } from "../../core/view";
export class BaseTextView extends View {
}
BaseTextView.__name__ = "BaseTextView";
export class BaseText extends Model {
    constructor(attrs) {
        super(attrs);
    }
}
_a = BaseText;
BaseText.__name__ = "BaseText";
(() => {
    _a.define(({ String }) => ({
        text: [String],
    }));
})();
//# sourceMappingURL=base_text.js.map