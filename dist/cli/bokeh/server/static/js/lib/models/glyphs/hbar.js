var _a;
import { Box, BoxView } from "./box";
import { ScreenArray } from "../../core/types";
import * as p from "../../core/properties";
export class HBarView extends BoxView {
    scenterxy(i) {
        const scx = (this.sleft[i] + this.sright[i]) / 2;
        const scy = this.sy[i];
        return [scx, scy];
    }
    _lrtb(i) {
        const left_i = this._left[i];
        const right_i = this._right[i];
        const y_i = this._y[i];
        const half_height_i = this.height.get(i) / 2;
        const l = Math.min(left_i, right_i);
        const r = Math.max(left_i, right_i);
        const t = y_i + half_height_i;
        const b = y_i - half_height_i;
        return [l, r, t, b];
    }
    _map_data() {
        this.sy = this.renderer.yscale.v_compute(this._y);
        this.sh = this.sdist(this.renderer.yscale, this._y, this.height, "center");
        this.sleft = this.renderer.xscale.v_compute(this._left);
        this.sright = this.renderer.xscale.v_compute(this._right);
        const n = this.sy.length;
        this.stop = new ScreenArray(n);
        this.sbottom = new ScreenArray(n);
        for (let i = 0; i < n; i++) {
            this.stop[i] = this.sy[i] - this.sh[i] / 2;
            this.sbottom[i] = this.sy[i] + this.sh[i] / 2;
        }
        this._clamp_viewport();
    }
}
HBarView.__name__ = "HBarView";
export class HBar extends Box {
    constructor(attrs) {
        super(attrs);
    }
}
_a = HBar;
HBar.__name__ = "HBar";
(() => {
    _a.prototype.default_view = HBarView;
    _a.define(({}) => ({
        left: [p.XCoordinateSpec, { value: 0 }],
        y: [p.YCoordinateSpec, { field: "y" }],
        height: [p.NumberSpec, { value: 1 }],
        right: [p.XCoordinateSpec, { field: "right" }],
    }));
})();
//# sourceMappingURL=hbar.js.map