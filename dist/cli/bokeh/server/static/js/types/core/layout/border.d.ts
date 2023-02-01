import { SizeHint, Size, Margin } from "./types";
import { Layoutable } from "./layoutable";
import { BBox } from "../util/bbox";
export declare class BorderLayout extends Layoutable {
    [Symbol.iterator](): Generator<Layoutable, void, unknown>;
    top_panel: Layoutable;
    bottom_panel: Layoutable;
    left_panel: Layoutable;
    right_panel: Layoutable;
    center_panel: Layoutable;
    min_border: Margin;
    padding: Margin;
    protected _measure(viewport: Size): SizeHint;
    protected _set_geometry(outer: BBox, inner: BBox): void;
}
//# sourceMappingURL=border.d.ts.map