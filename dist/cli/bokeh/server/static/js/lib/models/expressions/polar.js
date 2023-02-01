var _a;
import { CoordinateTransform } from "../expressions/coordinate_transform";
import { Direction } from "../../core/enums";
import * as p from "../../core/properties";
export class PolarTransform extends CoordinateTransform {
    constructor(attrs) {
        super(attrs);
    }
    _v_compute(source) {
        const radius = this.properties.radius.uniform(source);
        const angle = this.properties.angle.uniform(source);
        const coeff = this.direction == "anticlock" ? -1 : 1;
        const n = Math.min(radius.length, angle.length);
        const x = new Float64Array(n);
        const y = new Float64Array(n);
        for (let i = 0; i < n; i++) {
            const radius_i = radius.get(i);
            const angle_i = angle.get(i) * coeff;
            x[i] = radius_i * Math.cos(angle_i);
            y[i] = radius_i * Math.sin(angle_i);
        }
        return { x, y };
    }
}
_a = PolarTransform;
PolarTransform.__name__ = "PolarTransform";
(() => {
    _a.define(({}) => ({
        radius: [p.DistanceSpec, { field: "radius" }],
        angle: [p.AngleSpec, { field: "angle" }],
        direction: [Direction, "anticlock"],
    }));
})();
//# sourceMappingURL=polar.js.map