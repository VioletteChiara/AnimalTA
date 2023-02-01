var _a;
import { Box, BoxView } from "./box";
import { Column as ColumnLayout } from "../../core/layout/grid";
export class ColumnView extends BoxView {
    _update_layout() {
        const items = this.child_views.map((child) => child.layout);
        this.layout = new ColumnLayout(items);
        this.layout.rows = this.model.rows;
        this.layout.spacing = [this.model.spacing, 0];
        this.layout.set_sizing(this.box_sizing());
    }
}
ColumnView.__name__ = "ColumnView";
export class Column extends Box {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Column;
Column.__name__ = "Column";
(() => {
    _a.prototype.default_view = ColumnView;
    _a.define(({ Any }) => ({
        rows: [Any /*TODO*/, "auto"],
    }));
})();
//# sourceMappingURL=column.js.map