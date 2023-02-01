var _a;
import { XYGlyph, XYGlyphView } from "./xy_glyph";
import { generic_area_scalar_legend } from "./utils";
import * as hittest from "../../core/hittest";
import * as mixins from "../../core/property_mixins";
import { Selection } from "../selections/selection";
export class PatchView extends XYGlyphView {
    _render(ctx, indices, data) {
        const { sx, sy } = data ?? this;
        let move = true;
        ctx.beginPath();
        for (const i of indices) {
            const sx_i = sx[i];
            const sy_i = sy[i];
            if (!isFinite(sx_i + sy_i)) {
                ctx.closePath();
                move = true;
            }
            else {
                if (move) {
                    ctx.moveTo(sx_i, sy_i);
                    move = false;
                }
                else
                    ctx.lineTo(sx_i, sy_i);
            }
        }
        ctx.closePath();
        this.visuals.fill.apply(ctx);
        this.visuals.hatch.apply(ctx);
        this.visuals.line.apply(ctx);
    }
    draw_legend_for_index(ctx, bbox, _index) {
        generic_area_scalar_legend(this.visuals, ctx, bbox);
    }
    _hit_point(geometry) {
        const result = new Selection();
        if (hittest.point_in_poly(geometry.sx, geometry.sy, this.sx, this.sy)) {
            result.add_to_selected_glyphs(this.model);
            result.view = this;
        }
        return result;
    }
}
PatchView.__name__ = "PatchView";
export class Patch extends XYGlyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Patch;
Patch.__name__ = "Patch";
(() => {
    _a.prototype.default_view = PatchView;
    _a.mixins([mixins.LineScalar, mixins.FillScalar, mixins.HatchScalar]);
})();
//# sourceMappingURL=patch.js.map