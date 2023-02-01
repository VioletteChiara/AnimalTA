import { Annotation, AnnotationView } from "./annotation";
import * as mixins from "../../core/property_mixins";
import * as visuals from "../../core/visuals";
import { SpatialUnits } from "../../core/enums";
import * as p from "../../core/properties";
export declare class PolyAnnotationView extends AnnotationView {
    model: PolyAnnotation;
    visuals: PolyAnnotation.Visuals;
    connect_signals(): void;
    protected _render(): void;
}
export declare namespace PolyAnnotation {
    type Attrs = p.AttrsOf<Props>;
    type Props = Annotation.Props & {
        xs: p.Property<number[]>;
        xs_units: p.Property<SpatialUnits>;
        ys: p.Property<number[]>;
        ys_units: p.Property<SpatialUnits>;
        screen: p.Property<boolean>;
    } & Mixins;
    type Mixins = mixins.Line & mixins.Fill & mixins.Hatch;
    type Visuals = Annotation.Visuals & {
        line: visuals.Line;
        fill: visuals.Fill;
        hatch: visuals.Hatch;
    };
}
export interface PolyAnnotation extends PolyAnnotation.Attrs {
}
export declare class PolyAnnotation extends Annotation {
    properties: PolyAnnotation.Props;
    __view_type__: PolyAnnotationView;
    constructor(attrs?: Partial<PolyAnnotation.Attrs>);
    update({ xs, ys }: {
        xs: number[];
        ys: number[];
    }): void;
}
//# sourceMappingURL=poly_annotation.d.ts.map