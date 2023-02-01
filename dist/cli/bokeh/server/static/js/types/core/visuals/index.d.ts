import { Line, LineScalar, LineVector } from "./line";
import { Fill, FillScalar, FillVector } from "./fill";
import { Text, TextScalar, TextVector } from "./text";
import { Hatch, HatchScalar, HatchVector } from "./hatch";
export { Line, LineScalar, LineVector };
export { Fill, FillScalar, FillVector };
export { Text, TextScalar, TextVector };
export { Hatch, HatchScalar, HatchVector };
import { View } from "../view";
import { VisualProperties, VisualUniforms, Renderable } from "./visual";
export { VisualProperties, VisualUniforms, Renderable };
export declare class Visuals {
    [Symbol.iterator](): Generator<VisualProperties | VisualUniforms, void, undefined>;
    protected _visuals: (VisualProperties | VisualUniforms)[];
    constructor(view: View & Renderable);
}
//# sourceMappingURL=index.d.ts.map