var _a;
import { Filter } from "./filter";
import { Indices } from "../../core/types";
export class BooleanFilter extends Filter {
    constructor(attrs) {
        super(attrs);
    }
    compute_indices(source) {
        const size = source.length;
        const { booleans } = this;
        if (booleans == null) {
            return Indices.all_set(size);
        }
        else {
            return Indices.from_booleans(size, booleans);
        }
    }
}
_a = BooleanFilter;
BooleanFilter.__name__ = "BooleanFilter";
(() => {
    _a.define(({ Boolean, Array, Nullable }) => ({
        booleans: [Nullable(Array(Boolean)), null],
    }));
})();
//# sourceMappingURL=boolean_filter.js.map