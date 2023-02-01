var _a;
import { UpperLower, UpperLowerView } from "./upper_lower";
import * as mixins from "../../core/property_mixins";
export class BandView extends UpperLowerView {
    paint(ctx) {
        // Draw the band body
        ctx.beginPath();
        ctx.moveTo(this._lower_sx[0], this._lower_sy[0]);
        for (let i = 0, end = this._lower_sx.length; i < end; i++) {
            ctx.lineTo(this._lower_sx[i], this._lower_sy[i]);
        }
        // iterate backwards so that the upper end is below the lower start
        for (let i = this._upper_sx.length - 1; i >= 0; i--) {
            ctx.lineTo(this._upper_sx[i], this._upper_sy[i]);
        }
        ctx.closePath();
        this.visuals.fill.apply(ctx);
        // Draw the lower band edge
        ctx.beginPath();
        ctx.moveTo(this._lower_sx[0], this._lower_sy[0]);
        for (let i = 0, end = this._lower_sx.length; i < end; i++) {
            ctx.lineTo(this._lower_sx[i], this._lower_sy[i]);
        }
        this.visuals.line.apply(ctx);
        // Draw the upper band edge
        ctx.beginPath();
        ctx.moveTo(this._upper_sx[0], this._upper_sy[0]);
        for (let i = 0, end = this._upper_sx.length; i < end; i++) {
            ctx.lineTo(this._upper_sx[i], this._upper_sy[i]);
        }
        this.visuals.line.apply(ctx);
    }
}
BandView.__name__ = "BandView";
export class Band extends UpperLower {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Band;
Band.__name__ = "Band";
(() => {
    _a.prototype.default_view = BandView;
    _a.mixins([mixins.Line, mixins.Fill]);
    _a.override({
        fill_color: "#fff9ba",
        fill_alpha: 0.4,
        line_color: "#cccccc",
        line_alpha: 0.3,
    });
})();
//# sourceMappingURL=band.js.map