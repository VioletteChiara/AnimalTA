var _a;
import { inplace } from "../../core/util/projections";
import * as p from "../../core/properties";
import { Glyph, GlyphView } from "./glyph";
export class XYGlyphView extends GlyphView {
    _project_data() {
        inplace.project_xy(this._x, this._y);
    }
    _index_data(index) {
        const { _x, _y, data_size } = this;
        for (let i = 0; i < data_size; i++) {
            const x = _x[i];
            const y = _y[i];
            index.add_point(x, y);
        }
    }
    scenterxy(i) {
        return [this.sx[i], this.sy[i]];
    }
}
XYGlyphView.__name__ = "XYGlyphView";
export class XYGlyph extends Glyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = XYGlyph;
XYGlyph.__name__ = "XYGlyph";
(() => {
    _a.define(({}) => ({
        x: [p.XCoordinateSpec, { field: "x" }],
        y: [p.YCoordinateSpec, { field: "y" }],
    }));
})();
//# sourceMappingURL=xy_glyph.js.map