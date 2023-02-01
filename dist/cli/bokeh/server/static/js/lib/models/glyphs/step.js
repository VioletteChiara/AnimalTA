var _a;
import { XYGlyph, XYGlyphView } from "./xy_glyph";
import { generic_line_scalar_legend } from "./utils";
import * as mixins from "../../core/property_mixins";
import { StepMode } from "../../core/enums";
import { unreachable } from "../../core/util/assert";
export class StepView extends XYGlyphView {
    _render(ctx, indices, data) {
        const { sx, sy } = data ?? this;
        let drawing = false;
        let last_index = null;
        this.visuals.line.set_value(ctx);
        const L = indices.length;
        if (L < 2)
            return;
        ctx.beginPath();
        ctx.moveTo(sx[0], sy[0]);
        for (const i of indices) {
            let x1, x2;
            let y1, y2;
            switch (this.model.mode) {
                case "before": {
                    [x1, y1] = [sx[i - 1], sy[i]];
                    [x2, y2] = [sx[i], sy[i]];
                    break;
                }
                case "after": {
                    [x1, y1] = [sx[i], sy[i - 1]];
                    [x2, y2] = [sx[i], sy[i]];
                    break;
                }
                case "center": {
                    const xm = (sx[i - 1] + sx[i]) / 2;
                    [x1, y1] = [xm, sy[i - 1]];
                    [x2, y2] = [xm, sy[i]];
                    break;
                }
                default:
                    unreachable();
            }
            if (drawing) {
                if (!isFinite(sx[i] + sy[i])) {
                    ctx.stroke();
                    ctx.beginPath();
                    drawing = false;
                    last_index = i;
                    continue;
                }
                if (last_index != null && i - last_index > 1) {
                    ctx.stroke();
                    drawing = false;
                }
            }
            if (drawing) {
                ctx.lineTo(x1, y1);
                ctx.lineTo(x2, y2);
            }
            else {
                ctx.beginPath();
                ctx.moveTo(sx[i], sy[i]);
                drawing = true;
            }
            last_index = i;
        }
        ctx.lineTo(sx[L - 1], sy[L - 1]);
        ctx.stroke();
    }
    draw_legend_for_index(ctx, bbox, _index) {
        generic_line_scalar_legend(this.visuals, ctx, bbox);
    }
}
StepView.__name__ = "StepView";
export class Step extends XYGlyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Step;
Step.__name__ = "Step";
(() => {
    _a.prototype.default_view = StepView;
    _a.mixins(mixins.LineScalar);
    _a.define(() => ({
        mode: [StepMode, "before"],
    }));
})();
//# sourceMappingURL=step.js.map