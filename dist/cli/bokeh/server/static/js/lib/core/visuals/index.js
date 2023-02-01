import { Line, LineScalar, LineVector } from "./line";
import { Fill, FillScalar, FillVector } from "./fill";
import { Text, TextScalar, TextVector } from "./text";
import { Hatch, HatchScalar, HatchVector } from "./hatch";
export { Line, LineScalar, LineVector };
export { Fill, FillScalar, FillVector };
export { Text, TextScalar, TextVector };
export { Hatch, HatchScalar, HatchVector };
import * as mixins from "../property_mixins";
import { VisualProperties, VisualUniforms } from "./visual";
export { VisualProperties, VisualUniforms };
export class Visuals {
    constructor(view) {
        this._visuals = [];
        for (const [prefix, mixin] of view.model._mixins) {
            const visual = (() => {
                switch (mixin) {
                    case mixins.Line: return new Line(view, prefix);
                    case mixins.LineScalar: return new LineScalar(view, prefix);
                    case mixins.LineVector: return new LineVector(view, prefix);
                    case mixins.Fill: return new Fill(view, prefix);
                    case mixins.FillScalar: return new FillScalar(view, prefix);
                    case mixins.FillVector: return new FillVector(view, prefix);
                    case mixins.Text: return new Text(view, prefix);
                    case mixins.TextScalar: return new TextScalar(view, prefix);
                    case mixins.TextVector: return new TextVector(view, prefix);
                    case mixins.Hatch: return new Hatch(view, prefix);
                    case mixins.HatchScalar: return new HatchScalar(view, prefix);
                    case mixins.HatchVector: return new HatchVector(view, prefix);
                    default:
                        throw new Error("unknown visual");
                }
            })();
            if (visual instanceof VisualProperties)
                visual.update();
            this._visuals.push(visual);
            Object.defineProperty(this, prefix + visual.type, {
                get() { return visual; },
                configurable: false,
                enumerable: true,
            });
        }
    }
    *[Symbol.iterator]() {
        yield* this._visuals;
    }
}
Visuals.__name__ = "Visuals";
//# sourceMappingURL=index.js.map