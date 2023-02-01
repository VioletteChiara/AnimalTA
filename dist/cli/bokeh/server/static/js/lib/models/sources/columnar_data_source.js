var _a;
import { DataSource } from "./data_source";
import { Signal, Signal0 } from "../../core/signaling";
import { logger } from "../../core/logging";
import { SelectionManager } from "../../core/selection_manager";
import { isArray } from "../../core/util/types";
import { uniq } from "../../core/util/array";
import { keys, values } from "../../core/util/object";
import { Selection } from "../selections/selection";
import { SelectionPolicy, UnionRenderers } from "../selections/interaction_policy";
import { is_NDArray } from "../../core/util/ndarray";
export class ColumnarDataSource extends DataSource {
    constructor(attrs) {
        super(attrs);
        this.selection_manager = new SelectionManager(this);
    }
    get_array(key) {
        let column = this.data[key];
        if (column == null)
            this.data[key] = column = [];
        else if (!isArray(column))
            this.data[key] = column = Array.from(column);
        return column;
    }
    initialize() {
        super.initialize();
        this._select = new Signal0(this, "select");
        this.inspect = new Signal(this, "inspect");
        this.streaming = new Signal0(this, "streaming");
        this.patching = new Signal(this, "patching");
    }
    get_column(colname) {
        const column = this.data[colname];
        return column != null ? column : null;
    }
    columns() {
        // return the column names in this data source
        return keys(this.data);
    }
    get_length(soft = true) {
        const lengths = uniq(values(this.data).map((v) => is_NDArray(v) ? v.shape[0] : v.length));
        switch (lengths.length) {
            case 0: {
                return null; // XXX: don't guess, treat on case-by-case basis
            }
            case 1: {
                return lengths[0];
            }
            default: {
                const msg = "data source has columns of inconsistent lengths";
                if (soft) {
                    logger.warn(msg);
                    return lengths.sort()[0];
                }
                else
                    throw new Error(msg);
            }
        }
    }
    get length() {
        return this.get_length() ?? 0;
    }
    clear() {
        const empty = {};
        for (const col of this.columns()) {
            empty[col] = new this.data[col].constructor(0);
        }
        this.data = empty;
    }
}
_a = ColumnarDataSource;
ColumnarDataSource.__name__ = "ColumnarDataSource";
(() => {
    _a.define(({ Ref }) => ({
        selection_policy: [Ref(SelectionPolicy), () => new UnionRenderers()],
    }));
    _a.internal(({ AnyRef }) => ({
        inspected: [AnyRef(), () => new Selection()],
    }));
})();
//# sourceMappingURL=columnar_data_source.js.map