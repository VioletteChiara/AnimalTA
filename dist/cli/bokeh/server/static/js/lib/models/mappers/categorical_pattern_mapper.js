var _a;
import { cat_v_compute } from "./categorical_mapper";
import { FactorSeq } from "../ranges/factor_range";
import { Mapper } from "./mapper";
import { HatchPatternType } from "../../core/enums";
export class CategoricalPatternMapper extends Mapper {
    constructor(attrs) {
        super(attrs);
    }
    v_compute(xs) {
        const values = new Array(xs.length);
        cat_v_compute(xs, this.factors, this.patterns, values, this.start, this.end, this.default_value);
        return values;
    }
}
_a = CategoricalPatternMapper;
CategoricalPatternMapper.__name__ = "CategoricalPatternMapper";
(() => {
    _a.define(({ Number, Array, Nullable }) => ({
        factors: [FactorSeq],
        patterns: [Array(HatchPatternType)],
        start: [Number, 0],
        end: [Nullable(Number), null],
        default_value: [HatchPatternType, " "],
    }));
})();
//# sourceMappingURL=categorical_pattern_mapper.js.map