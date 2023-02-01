var _a;
import { Glyph, GlyphView } from "./glyph";
import { generic_area_scalar_legend } from "./utils";
import * as mixins from "../../core/property_mixins";
export class AreaView extends GlyphView {
    draw_legend_for_index(ctx, bbox, _index) {
        generic_area_scalar_legend(this.visuals, ctx, bbox);
    }
}
AreaView.__name__ = "AreaView";
export class Area extends Glyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Area;
Area.__name__ = "Area";
(() => {
    _a.mixins([mixins.FillScalar, mixins.HatchScalar]);
})();
//# sourceMappingURL=area.js.map