var _a;
import { LayoutDOM, LayoutDOMView } from "./layout_dom";
import { Grid } from "../../core/layout/grid";
export class GridBoxView extends LayoutDOMView {
    connect_signals() {
        super.connect_signals();
        const { children, rows, cols, spacing } = this.model.properties;
        this.on_change([children, rows, cols, spacing], () => this.rebuild());
    }
    get child_models() {
        return this.model.children.map(([child]) => child);
    }
    _update_layout() {
        this.layout = new Grid();
        this.layout.rows = this.model.rows;
        this.layout.cols = this.model.cols;
        this.layout.spacing = this.model.spacing;
        for (const [child, row, col, row_span, col_span] of this.model.children) {
            const child_view = this._child_views.get(child);
            this.layout.items.push({ layout: child_view.layout, row, col, row_span, col_span });
        }
        this.layout.set_sizing(this.box_sizing());
    }
}
GridBoxView.__name__ = "GridBoxView";
export class GridBox extends LayoutDOM {
    constructor(attrs) {
        super(attrs);
    }
}
_a = GridBox;
GridBox.__name__ = "GridBox";
(() => {
    _a.prototype.default_view = GridBoxView;
    _a.define(({ Any, Int, Number, Tuple, Array, Ref, Or, Opt }) => ({
        children: [Array(Tuple(Ref(LayoutDOM), Int, Int, Opt(Int), Opt(Int))), []],
        rows: [Any /*TODO*/, "auto"],
        cols: [Any /*TODO*/, "auto"],
        spacing: [Or(Number, Tuple(Number, Number)), 0],
    }));
})();
//# sourceMappingURL=grid_box.js.map