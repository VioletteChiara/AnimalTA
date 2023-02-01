var _a;
import { Column, ColumnView } from "./column";
export class WidgetBoxView extends ColumnView {
}
WidgetBoxView.__name__ = "WidgetBoxView";
export class WidgetBox extends Column {
    constructor(attrs) {
        super(attrs);
    }
}
_a = WidgetBox;
WidgetBox.__name__ = "WidgetBox";
(() => {
    _a.prototype.default_view = WidgetBoxView;
})();
//# sourceMappingURL=widget_box.js.map