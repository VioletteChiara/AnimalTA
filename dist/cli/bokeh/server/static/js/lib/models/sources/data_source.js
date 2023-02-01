var _a;
import { Model } from "../../model";
import { Selection } from "../selections/selection";
export class DataSource extends Model {
    constructor(attrs) {
        super(attrs);
    }
}
_a = DataSource;
DataSource.__name__ = "DataSource";
(() => {
    _a.define(({ Ref }) => ({
        selected: [Ref(Selection), () => new Selection()],
    }));
})();
//# sourceMappingURL=data_source.js.map