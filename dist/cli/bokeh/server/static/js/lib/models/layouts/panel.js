var _a;
import { Model } from "../../model";
import { LayoutDOM } from "./layout_dom";
export class Panel extends Model {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Panel;
Panel.__name__ = "Panel";
(() => {
    _a.define(({ Boolean, String, Ref }) => ({
        title: [String, ""],
        child: [Ref(LayoutDOM)],
        closable: [Boolean, false],
        disabled: [Boolean, false],
    }));
})();
//# sourceMappingURL=panel.js.map