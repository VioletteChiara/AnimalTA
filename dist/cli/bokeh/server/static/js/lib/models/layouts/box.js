var _a;
import { LayoutDOM, LayoutDOMView } from "./layout_dom";
export class BoxView extends LayoutDOMView {
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.properties.children.change, () => this.rebuild());
    }
    get child_models() {
        return this.model.children;
    }
}
BoxView.__name__ = "BoxView";
export class Box extends LayoutDOM {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Box;
Box.__name__ = "Box";
(() => {
    _a.define(({ Number, Array, Ref }) => ({
        children: [Array(Ref(LayoutDOM)), []],
        spacing: [Number, 0],
    }));
})();
//# sourceMappingURL=box.js.map