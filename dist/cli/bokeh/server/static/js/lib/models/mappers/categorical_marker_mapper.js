var _a;
import { cat_v_compute } from "./categorical_mapper";
import { FactorSeq } from "../ranges/factor_range";
import { Mapper } from "./mapper";
import { MarkerType } from "../../core/enums";
export class CategoricalMarkerMapper extends Mapper {
    constructor(attrs) {
        super(attrs);
    }
    v_compute(xs) {
        const values = new Array(xs.length);
        cat_v_compute(xs, this.factors, this.markers, values, this.start, this.end, this.default_value);
        return values;
    }
}
_a = CategoricalMarkerMapper;
CategoricalMarkerMapper.__name__ = "CategoricalMarkerMapper";
(() => {
    _a.define(({ Number, Array, Nullable }) => ({
        factors: [FactorSeq],
        markers: [Array(MarkerType)],
        start: [Number, 0],
        end: [Nullable(Number), null],
        default_value: [MarkerType, "circle"],
    }));
})();
//# sourceMappingURL=categorical_marker_mapper.js.map