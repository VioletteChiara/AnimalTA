var _a;
import { Model } from "../../model";
import { Indices } from "../../core/types";
import { Filter } from "../filters/filter";
import { ColumnarDataSource } from "./columnar_data_source";
export class CDSView extends Model {
    constructor(attrs) {
        super(attrs);
    }
    initialize() {
        super.initialize();
        this.compute_indices();
    }
    connect_signals() {
        super.connect_signals();
        this.connect(this.properties.filters.change, () => this.compute_indices());
        const connect_listeners = () => {
            const fn = () => this.compute_indices();
            if (this.source != null) {
                this.connect(this.source.change, fn);
                if (this.source instanceof ColumnarDataSource) {
                    this.connect(this.source.streaming, fn);
                    this.connect(this.source.patching, fn);
                }
            }
        };
        let initialized = this.source != null;
        if (initialized)
            connect_listeners();
        else {
            this.connect(this.properties.source.change, () => {
                if (!initialized) {
                    connect_listeners();
                    initialized = true;
                }
            });
        }
    }
    compute_indices() {
        const { source } = this;
        if (source == null)
            return;
        // XXX: if the data source is empty, there still may be one
        // index originating from glyph's scalar values.
        const size = source.get_length() ?? 1;
        const indices = Indices.all_set(size);
        for (const filter of this.filters) {
            indices.intersect(filter.compute_indices(source));
        }
        this.indices = indices;
        this._indices = [...indices];
        this.indices_map_to_subset();
    }
    indices_map_to_subset() {
        this.indices_map = {};
        for (let i = 0; i < this._indices.length; i++) {
            this.indices_map[this._indices[i]] = i;
        }
    }
    convert_selection_from_subset(selection_subset) {
        return selection_subset.map((i) => this._indices[i]);
    }
    convert_selection_to_subset(selection_full) {
        return selection_full.map((i) => this.indices_map[i]);
    }
    convert_indices_from_subset(indices) {
        return indices.map((i) => this._indices[i]);
    }
}
_a = CDSView;
CDSView.__name__ = "CDSView";
(() => {
    _a.define(({ Array, Ref }) => ({
        filters: [Array(Ref(Filter)), []],
        source: [Ref(ColumnarDataSource)],
    }));
    _a.internal(({ Int, Dict, Ref, Nullable }) => ({
        indices: [Ref(Indices)],
        indices_map: [Dict(Int), {}],
        masked: [Nullable(Ref(Indices)), null],
    }));
})();
//# sourceMappingURL=cds_view.js.map