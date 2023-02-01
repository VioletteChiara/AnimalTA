var _a;
import { Box, BoxView } from "./box";
import { ScreenArray } from "../../core/types";
import * as p from "../../core/properties";
export class VBarView extends BoxView {
    scenterxy(i) {
        const scx = this.sx[i];
        const scy = (this.stop[i] + this.sbottom[i]) / 2;
        return [scx, scy];
    }
    _lrtb(i) {
        const half_width_i = this.width.get(i) / 2;
        const x_i = this._x[i];
        const top_i = this._top[i];
        const bottom_i = this._bottom[i];
        const l = x_i - half_width_i;
        const r = x_i + half_width_i;
        const t = Math.max(top_i, bottom_i);
        const b = Math.min(top_i, bottom_i);
        return [l, r, t, b];
    }
    _map_data() {
        this.sx = this.renderer.xscale.v_compute(this._x);
        this.sw = this.sdist(this.renderer.xscale, this._x, this.width, "center");
        this.stop = this.renderer.yscale.v_compute(this._top);
        this.sbottom = this.renderer.yscale.v_compute(this._bottom);
        const n = this.sx.length;
        this.sleft = new ScreenArray(n);
        this.sright = new ScreenArray(n);
        for (let i = 0; i < n; i++) {
            this.sleft[i] = this.sx[i] - this.sw[i] / 2;
            this.sright[i] = this.sx[i] + this.sw[i] / 2;
        }
        this._clamp_viewport();
    }
}
VBarView.__name__ = "VBarView";
export class VBar extends Box {
    constructor(attrs) {
        super(attrs);
    }
}
_a = VBar;
VBar.__name__ = "VBar";
(() => {
    _a.prototype.default_view = VBarView;
    _a.define(({}) => ({
        x: [p.XCoordinateSpec, { field: "x" }],
        bottom: [p.YCoordinateSpec, { value: 0 }],
        width: [p.NumberSpec, { value: 1 }],
        top: [p.YCoordinateSpec, { field: "top" }],
    }));
})();
//# sourceMappingURL=vbar.js.map