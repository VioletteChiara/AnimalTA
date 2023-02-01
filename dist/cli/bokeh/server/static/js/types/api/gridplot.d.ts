import { LayoutDOM } from "./models";
import { SizingMode, Location } from "../core/enums";
import { Matrix } from "../core/util/matrix";
export declare type GridPlotOpts = {
    toolbar_location?: Location | null;
    merge_tools?: boolean;
    sizing_mode?: SizingMode;
    width?: number;
    height?: number;
    /** @deprecated */
    plot_width?: number;
    /** @deprecated */
    plot_height?: number;
};
export declare function gridplot(children: (LayoutDOM | null)[][] | Matrix<LayoutDOM | null>, options?: GridPlotOpts): LayoutDOM;
//# sourceMappingURL=gridplot.d.ts.map