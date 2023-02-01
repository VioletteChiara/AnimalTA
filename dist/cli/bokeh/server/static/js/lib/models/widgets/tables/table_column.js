var _a;
import { StringFormatter } from "./cell_formatters";
import { StringEditor } from "./cell_editors";
import { uniqueId } from "../../../core/util/string";
import { Sort } from "../../../core/enums";
import { Model } from "../../../model";
export class TableColumn extends Model {
    constructor(attrs) {
        super(attrs);
    }
    toColumn() {
        return {
            id: uniqueId(),
            field: this.field,
            name: this.title ?? this.field,
            width: this.width,
            formatter: this.formatter != null ? this.formatter.doFormat.bind(this.formatter) : undefined,
            model: this.editor,
            editor: this.editor.default_view,
            sortable: this.sortable,
            defaultSortAsc: this.default_sort == "ascending",
        };
    }
}
_a = TableColumn;
TableColumn.__name__ = "TableColumn";
(() => {
    _a.define(({ Boolean, Number, String, Nullable, Ref }) => ({
        field: [String],
        title: [Nullable(String), null],
        width: [Number, 300],
        formatter: [Ref(StringFormatter), () => new StringFormatter()],
        editor: [Ref(StringEditor), () => new StringEditor()],
        sortable: [Boolean, true],
        default_sort: [Sort, "ascending"],
        visible: [Boolean, true],
    }));
})();
//# sourceMappingURL=table_column.js.map