var _a;
import { RangeTransform } from "./range_transform";
export class Dodge extends RangeTransform {
    constructor(attrs) {
        super(attrs);
    }
    _compute(x) {
        return x + this.value;
    }
}
_a = Dodge;
Dodge.__name__ = "Dodge";
(() => {
    _a.define(({ Number }) => ({
        value: [Number, 0],
    }));
})();
//# sourceMappingURL=dodge.js.map