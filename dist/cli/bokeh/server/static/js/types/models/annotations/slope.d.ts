import { Annotation, AnnotationView } from "./annotation";
import * as mixins from "../../core/property_mixins";
import * as visuals from "../../core/visuals";
import * as p from "../../core/properties";
export declare class SlopeView extends AnnotationView {
    model: Slope;
    visuals: Slope.Visuals;
    connect_signals(): void;
    protected _render(): void;
}
export declare namespace Slope {
    type Attrs = p.AttrsOf<Props>;
    type Props = Annotation.Props & {
        gradient: p.Property<number | null>;
        y_intercept: p.Property<number | null>;
    } & Mixins;
    type Mixins = mixins.Line;
    type Visuals = Annotation.Visuals & {
        line: visuals.Line;
    };
}
export interface Slope extends Slope.Attrs {
}
export declare class Slope extends Annotation {
    properties: Slope.Props;
    __view_type__: SlopeView;
    constructor(attrs?: Partial<Slope.Attrs>);
}
//# sourceMappingURL=slope.d.ts.map