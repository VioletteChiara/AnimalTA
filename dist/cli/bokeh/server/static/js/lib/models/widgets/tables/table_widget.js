var _a;
import { Widget } from "../widget";
import { ColumnDataSource } from "../../sources/column_data_source";
import { CDSView } from "../../sources/cds_view";
export class TableWidget extends Widget {
    constructor(attrs) {
        super(attrs);
    }
    initialize() {
        super.initialize();
        if (this.view.source == null) {
            this.view.source = this.source;
            this.view.compute_indices();
        }
    }
}
_a = TableWidget;
TableWidget.__name__ = "TableWidget";
(() => {
    _a.define(({ Ref }) => ({
        source: [Ref(ColumnDataSource), () => new ColumnDataSource()],
        view: [Ref(CDSView), () => new CDSView()],
    }));
})();
//# sourceMappingURL=table_widget.js.map