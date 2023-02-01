var _a;
import { cat_v_compute } from "./categorical_mapper";
import { ColorMapper } from "./color_mapper";
import { FactorSeq } from "../ranges/factor_range";
export class CategoricalColorMapper extends ColorMapper {
    constructor(attrs) {
        super(attrs);
    }
    _v_compute(data, values, palette, { nan_color }) {
        cat_v_compute(data, this.factors, palette, values, this.start, this.end, nan_color);
    }
}
_a = CategoricalColorMapper;
CategoricalColorMapper.__name__ = "CategoricalColorMapper";
(() => {
    _a.define(({ Number, Nullable }) => ({
        factors: [FactorSeq],
        start: [Number, 0],
        end: [Nullable(Number), null],
    }));
})();
//# sourceMappingURL=categorical_color_mapper.js.map