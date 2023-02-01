var _a;
import { ScreenArray } from "../../core/types";
import { Area, AreaView } from "./area";
import * as hittest from "../../core/hittest";
import * as p from "../../core/properties";
import { Selection } from "../selections/selection";
export class HAreaView extends AreaView {
    _index_data(index) {
        const { min, max } = Math;
        const { data_size } = this;
        for (let i = 0; i < data_size; i++) {
            const x1 = this._x1[i];
            const x2 = this._x2[i];
            const y = this._y[i];
            index.add_rect(min(x1, x2), y, max(x1, x2), y);
        }
    }
    _render(ctx, _indices, data) {
        const { sx1, sx2, sy } = data ?? this;
        ctx.beginPath();
        for (let i = 0, end = sx1.length; i < end; i++) {
            ctx.lineTo(sx1[i], sy[i]);
        }
        // iterate backwards so that the upper end is below the lower start
        for (let i = sx2.length - 1; i >= 0; i--) {
            ctx.lineTo(sx2[i], sy[i]);
        }
        ctx.closePath();
        this.visuals.fill.apply(ctx);
        this.visuals.hatch.apply(ctx);
    }
    _hit_point(geometry) {
        const L = this.sy.length;
        const sx = new ScreenArray(2 * L);
        const sy = new ScreenArray(2 * L);
        for (let i = 0, end = L; i < end; i++) {
            sx[i] = this.sx1[i];
            sy[i] = this.sy[i];
            sx[L + i] = this.sx2[L - i - 1];
            sy[L + i] = this.sy[L - i - 1];
        }
        const result = new Selection();
        if (hittest.point_in_poly(geometry.sx, geometry.sy, sx, sy)) {
            result.add_to_selected_glyphs(this.model);
            result.view = this;
        }
        return result;
    }
    scenterxy(i) {
        const scx = (this.sx1[i] + this.sx2[i]) / 2;
        const scy = this.sy[i];
        return [scx, scy];
    }
    _map_data() {
        this.sx1 = this.renderer.xscale.v_compute(this._x1);
        this.sx2 = this.renderer.xscale.v_compute(this._x2);
        this.sy = this.renderer.yscale.v_compute(this._y);
    }
}
HAreaView.__name__ = "HAreaView";
export class HArea extends Area {
    constructor(attrs) {
        super(attrs);
    }
}
_a = HArea;
HArea.__name__ = "HArea";
(() => {
    _a.prototype.default_view = HAreaView;
    _a.define(({}) => ({
        x1: [p.XCoordinateSpec, { field: "x1" }],
        x2: [p.XCoordinateSpec, { field: "x2" }],
        y: [p.YCoordinateSpec, { field: "y" }],
    }));
})();
//# sourceMappingURL=harea.js.map