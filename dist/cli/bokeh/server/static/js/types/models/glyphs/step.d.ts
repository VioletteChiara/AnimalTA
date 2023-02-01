import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import * as mixins from "../../core/property_mixins";
import * as visuals from "../../core/visuals";
import * as p from "../../core/properties";
import { Rect } from "../../core/types";
import { StepMode } from "../../core/enums";
import { Context2d } from "../../core/util/canvas";
export declare type StepData = XYGlyphData;
export interface StepView extends StepData {
}
export declare class StepView extends XYGlyphView {
    model: Step;
    visuals: Step.Visuals;
    protected _render(ctx: Context2d, indices: number[], data?: StepData): void;
    draw_legend_for_index(ctx: Context2d, bbox: Rect, _index: number): void;
}
export declare namespace Step {
    type Attrs = p.AttrsOf<Props>;
    type Props = XYGlyph.Props & {
        mode: p.Property<StepMode>;
    } & Mixins;
    type Mixins = mixins.LineScalar;
    type Visuals = XYGlyph.Visuals & {
        line: visuals.LineScalar;
    };
}
export interface Step extends Step.Attrs {
}
export declare class Step extends XYGlyph {
    properties: Step.Props;
    __view_type__: StepView;
    constructor(attrs?: Partial<Step.Attrs>);
}
//# sourceMappingURL=step.d.ts.map