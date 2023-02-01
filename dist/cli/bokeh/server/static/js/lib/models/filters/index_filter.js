var _a;
import { Filter } from "./filter";
import { Indices } from "../../core/types";
export class IndexFilter extends Filter {
    constructor(attrs) {
        super(attrs);
    }
    compute_indices(source) {
        const size = source.length;
        const { indices } = this;
        if (indices == null) {
            return Indices.all_set(size);
        }
        else {
            return Indices.from_indices(size, indices);
        }
    }
}
_a = IndexFilter;
IndexFilter.__name__ = "IndexFilter";
(() => {
    _a.define(({ Int, Array, Nullable }) => ({
        indices: [Nullable(Array(Int)), null],
    }));
})();
//# sourceMappingURL=index_filter.js.map