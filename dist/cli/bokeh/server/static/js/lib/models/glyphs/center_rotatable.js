var _a;
import { XYGlyph, XYGlyphView } from "./xy_glyph";
import { LineVector, FillVector, HatchVector } from "../../core/property_mixins";
import * as p from "../../core/properties";
export class CenterRotatableView extends XYGlyphView {
    get max_w2() {
        return this.model.properties.width.units == "data" ? this.max_width / 2 : 0;
    }
    get max_h2() {
        return this.model.properties.height.units == "data" ? this.max_height / 2 : 0;
    }
    _bounds({ x0, x1, y0, y1 }) {
        const { max_w2, max_h2 } = this;
        return {
            x0: x0 - max_w2,
            x1: x1 + max_w2,
            y0: y0 - max_h2,
            y1: y1 + max_h2,
        };
    }
}
CenterRotatableView.__name__ = "CenterRotatableView";
export class CenterRotatable extends XYGlyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = CenterRotatable;
CenterRotatable.__name__ = "CenterRotatable";
(() => {
    _a.mixins([LineVector, FillVector, HatchVector]);
    _a.define(({}) => ({
        angle: [p.AngleSpec, 0],
        width: [p.DistanceSpec, { field: "width" }],
        height: [p.DistanceSpec, { field: "height" }],
    }));
})();
//# sourceMappingURL=center_rotatable.js.map