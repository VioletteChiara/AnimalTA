import { Model } from "../../model";
import { LayoutDOM } from "./layout_dom";
import * as p from "../../core/properties";
export declare namespace Panel {
    type Attrs = p.AttrsOf<Props>;
    type Props = Model.Props & {
        title: p.Property<string>;
        child: p.Property<LayoutDOM>;
        closable: p.Property<boolean>;
        disabled: p.Property<boolean>;
    };
}
export interface Panel extends Panel.Attrs {
}
export declare class Panel extends Model {
    properties: Panel.Props;
    constructor(attrs?: Partial<Panel.Attrs>);
}
//# sourceMappingURL=panel.d.ts.map