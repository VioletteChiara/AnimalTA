var _a, _b, _c, _d, _e;
import { Model } from "../../model";
import { View } from "../../core/view";
import * as visuals from "../../core/visuals";
import { LineVector, FillVector } from "../../core/property_mixins";
import * as p from "../../core/properties";
export class ArrowHeadView extends View {
    initialize() {
        super.initialize();
        this.visuals = new visuals.Visuals(this);
    }
    request_render() {
        this.parent.request_render();
    }
    get canvas() {
        return this.parent.canvas;
    }
    set_data(source) {
        const self = this;
        for (const prop of this.model) {
            if (!(prop instanceof p.VectorSpec || prop instanceof p.ScalarSpec))
                continue;
            const uniform = prop.uniform(source);
            self[`${prop.attr}`] = uniform;
        }
    }
}
ArrowHeadView.__name__ = "ArrowHeadView";
export class ArrowHead extends Model {
    constructor(attrs) {
        super(attrs);
    }
}
_a = ArrowHead;
ArrowHead.__name__ = "ArrowHead";
(() => {
    _a.define(() => ({
        size: [p.NumberSpec, 25],
    }));
})();
export class OpenHeadView extends ArrowHeadView {
    clip(ctx, i) {
        this.visuals.line.set_vectorize(ctx, i);
        const size_i = this.size.get(i);
        ctx.moveTo(0.5 * size_i, size_i);
        ctx.lineTo(0.5 * size_i, -2);
        ctx.lineTo(-0.5 * size_i, -2);
        ctx.lineTo(-0.5 * size_i, size_i);
        ctx.lineTo(0, 0);
        ctx.lineTo(0.5 * size_i, size_i);
    }
    render(ctx, i) {
        if (this.visuals.line.doit) {
            this.visuals.line.set_vectorize(ctx, i);
            const size_i = this.size.get(i);
            ctx.beginPath();
            ctx.moveTo(0.5 * size_i, size_i);
            ctx.lineTo(0, 0);
            ctx.lineTo(-0.5 * size_i, size_i);
            ctx.stroke();
        }
    }
}
OpenHeadView.__name__ = "OpenHeadView";
export class OpenHead extends ArrowHead {
    constructor(attrs) {
        super(attrs);
    }
}
_b = OpenHead;
OpenHead.__name__ = "OpenHead";
(() => {
    _b.prototype.default_view = OpenHeadView;
    _b.mixins(LineVector);
})();
export class NormalHeadView extends ArrowHeadView {
    clip(ctx, i) {
        this.visuals.line.set_vectorize(ctx, i);
        const size_i = this.size.get(i);
        ctx.moveTo(0.5 * size_i, size_i);
        ctx.lineTo(0.5 * size_i, -2);
        ctx.lineTo(-0.5 * size_i, -2);
        ctx.lineTo(-0.5 * size_i, size_i);
        ctx.lineTo(0.5 * size_i, size_i);
    }
    render(ctx, i) {
        if (this.visuals.fill.doit) {
            this.visuals.fill.set_vectorize(ctx, i);
            this._normal(ctx, i);
            ctx.fill();
        }
        if (this.visuals.line.doit) {
            this.visuals.line.set_vectorize(ctx, i);
            this._normal(ctx, i);
            ctx.stroke();
        }
    }
    _normal(ctx, i) {
        const size_i = this.size.get(i);
        ctx.beginPath();
        ctx.moveTo(0.5 * size_i, size_i);
        ctx.lineTo(0, 0);
        ctx.lineTo(-0.5 * size_i, size_i);
        ctx.closePath();
    }
}
NormalHeadView.__name__ = "NormalHeadView";
export class NormalHead extends ArrowHead {
    constructor(attrs) {
        super(attrs);
    }
}
_c = NormalHead;
NormalHead.__name__ = "NormalHead";
(() => {
    _c.prototype.default_view = NormalHeadView;
    _c.mixins([LineVector, FillVector]);
    _c.override({
        fill_color: "black",
    });
})();
export class VeeHeadView extends ArrowHeadView {
    clip(ctx, i) {
        this.visuals.line.set_vectorize(ctx, i);
        const size_i = this.size.get(i);
        ctx.moveTo(0.5 * size_i, size_i);
        ctx.lineTo(0.5 * size_i, -2);
        ctx.lineTo(-0.5 * size_i, -2);
        ctx.lineTo(-0.5 * size_i, size_i);
        ctx.lineTo(0, 0.5 * size_i);
        ctx.lineTo(0.5 * size_i, size_i);
    }
    render(ctx, i) {
        if (this.visuals.fill.doit) {
            this.visuals.fill.set_vectorize(ctx, i);
            this._vee(ctx, i);
            ctx.fill();
        }
        if (this.visuals.line.doit) {
            this.visuals.line.set_vectorize(ctx, i);
            this._vee(ctx, i);
            ctx.stroke();
        }
    }
    _vee(ctx, i) {
        const size_i = this.size.get(i);
        ctx.beginPath();
        ctx.moveTo(0.5 * size_i, size_i);
        ctx.lineTo(0, 0);
        ctx.lineTo(-0.5 * size_i, size_i);
        ctx.lineTo(0, 0.5 * size_i);
        ctx.closePath();
    }
}
VeeHeadView.__name__ = "VeeHeadView";
export class VeeHead extends ArrowHead {
    constructor(attrs) {
        super(attrs);
    }
}
_d = VeeHead;
VeeHead.__name__ = "VeeHead";
(() => {
    _d.prototype.default_view = VeeHeadView;
    _d.mixins([LineVector, FillVector]);
    _d.override({
        fill_color: "black",
    });
})();
export class TeeHeadView extends ArrowHeadView {
    render(ctx, i) {
        if (this.visuals.line.doit) {
            this.visuals.line.set_vectorize(ctx, i);
            const size_i = this.size.get(i);
            ctx.beginPath();
            ctx.moveTo(0.5 * size_i, 0);
            ctx.lineTo(-0.5 * size_i, 0);
            ctx.stroke();
        }
    }
    clip(_ctx, _i) { }
}
TeeHeadView.__name__ = "TeeHeadView";
export class TeeHead extends ArrowHead {
    constructor(attrs) {
        super(attrs);
    }
}
_e = TeeHead;
TeeHead.__name__ = "TeeHead";
(() => {
    _e.prototype.default_view = TeeHeadView;
    _e.mixins(LineVector);
})();
//# sourceMappingURL=arrow_head.js.map