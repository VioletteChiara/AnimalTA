var _a;
import { Box, BoxView } from "./box";
import * as p from "../../core/properties";
export class QuadView extends BoxView {
    scenterxy(i) {
        const scx = this.sleft[i] / 2 + this.sright[i] / 2;
        const scy = this.stop[i] / 2 + this.sbottom[i] / 2;
        return [scx, scy];
    }
    _lrtb(i) {
        const l = this._left[i];
        const r = this._right[i];
        const t = this._top[i];
        const b = this._bottom[i];
        return [l, r, t, b];
    }
}
QuadView.__name__ = "QuadView";
export class Quad extends Box {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Quad;
Quad.__name__ = "Quad";
(() => {
    _a.prototype.default_view = QuadView;
    _a.define(({}) => ({
        right: [p.XCoordinateSpec, { field: "right" }],
        bottom: [p.YCoordinateSpec, { field: "bottom" }],
        left: [p.XCoordinateSpec, { field: "left" }],
        top: [p.YCoordinateSpec, { field: "top" }],
    }));
})();
//# sourceMappingURL=quad.js.map