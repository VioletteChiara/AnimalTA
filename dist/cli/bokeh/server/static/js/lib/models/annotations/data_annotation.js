var _a;
import { Annotation, AnnotationView } from "./annotation";
import { ColumnarDataSource } from "../sources/columnar_data_source";
import { ColumnDataSource } from "../sources/column_data_source";
import { inplace } from "../../core/util/projections";
import * as p from "../../core/properties";
export class DataAnnotationView extends AnnotationView {
    constructor() {
        super(...arguments);
        this._initial_set_data = false;
    }
    connect_signals() {
        super.connect_signals();
        const update = () => {
            this.set_data(this.model.source);
            this._rerender();
        };
        this.connect(this.model.change, update);
        this.connect(this.model.source.streaming, update);
        this.connect(this.model.source.patching, update);
        this.connect(this.model.source.change, update);
    }
    _rerender() {
        this.request_render();
    }
    set_data(source) {
        const self = this;
        for (const prop of this.model) {
            if (!(prop instanceof p.VectorSpec || prop instanceof p.ScalarSpec))
                continue;
            if (prop instanceof p.BaseCoordinateSpec) {
                const array = prop.array(source);
                self[`_${prop.attr}`] = array;
            }
            else {
                const uniform = prop.uniform(source);
                self[`${prop.attr}`] = uniform;
            }
        }
        if (this.plot_model.use_map) {
            if (self._x != null)
                inplace.project_xy(self._x, self._y);
            if (self._xs != null)
                inplace.project_xsys(self._xs, self._ys);
        }
        for (const visual of this.visuals) {
            visual.update();
        }
    }
    _render() {
        if (!this._initial_set_data) {
            this.set_data(this.model.source);
            this._initial_set_data = true;
        }
        this.map_data();
        this.paint(this.layer.ctx);
    }
}
DataAnnotationView.__name__ = "DataAnnotationView";
export class DataAnnotation extends Annotation {
    constructor(attrs) {
        super(attrs);
    }
}
_a = DataAnnotation;
DataAnnotation.__name__ = "DataAnnotation";
(() => {
    _a.define(({ Ref }) => ({
        source: [Ref(ColumnarDataSource), () => new ColumnDataSource()],
    }));
})();
//# sourceMappingURL=data_annotation.js.map