var _a;
import { Box, BoxView } from "./box";
import { Row as RowLayout } from "../../core/layout/grid";
export class RowView extends BoxView {
    _update_layout() {
        const items = this.child_views.map((child) => child.layout);
        this.layout = new RowLayout(items);
        this.layout.cols = this.model.cols;
        this.layout.spacing = [0, this.model.spacing];
        this.layout.set_sizing(this.box_sizing());
    }
}
RowView.__name__ = "RowView";
export class Row extends Box {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Row;
Row.__name__ = "Row";
(() => {
    _a.prototype.default_view = RowView;
    _a.define(({ Any }) => ({
        cols: [Any /*TODO*/, "auto"],
    }));
})();
//# sourceMappingURL=row.js.map