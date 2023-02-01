var _a;
import { Model } from "../../model";
import { union, intersection, difference } from "../../core/util/array";
import { merge, entries, to_object } from "../../core/util/object";
export class Selection extends Model {
    constructor(attrs) {
        super(attrs);
    }
    get_view() {
        return this.view;
    }
    get selected_glyph() {
        return this.selected_glyphs.length > 0 ? this.selected_glyphs[0] : null;
    }
    add_to_selected_glyphs(glyph) {
        this.selected_glyphs.push(glyph);
    }
    update(selection, _final = true, mode = "replace") {
        switch (mode) {
            case "replace": {
                this.indices = selection.indices;
                this.line_indices = selection.line_indices;
                this.multiline_indices = selection.multiline_indices;
                this.image_indices = selection.image_indices;
                this.view = selection.view;
                this.selected_glyphs = selection.selected_glyphs;
                break;
            }
            case "append": {
                this.update_through_union(selection);
                break;
            }
            case "intersect": {
                this.update_through_intersection(selection);
                break;
            }
            case "subtract": {
                this.update_through_subtraction(selection);
                break;
            }
        }
    }
    clear() {
        this.indices = [];
        this.line_indices = [];
        this.multiline_indices = {};
        this.image_indices = [];
        this.view = null;
        this.selected_glyphs = [];
    }
    map(mapper) {
        return new Selection({
            ...this.attributes,
            indices: this.indices.map(mapper),
            // NOTE: line_indices don't support subset indexing
            multiline_indices: to_object(entries(this.multiline_indices).map(([index, line_indices]) => [mapper(Number(index)), line_indices])),
            image_indices: this.image_indices.map((ndx) => ({ ...ndx, index: mapper(ndx.index) })),
        });
    }
    is_empty() {
        return this.indices.length == 0 && this.line_indices.length == 0 && this.image_indices.length == 0;
    }
    update_through_union(other) {
        this.indices = union(this.indices, other.indices);
        this.selected_glyphs = union(other.selected_glyphs, this.selected_glyphs);
        this.line_indices = union(other.line_indices, this.line_indices);
        this.view = other.view;
        this.multiline_indices = merge(other.multiline_indices, this.multiline_indices);
    }
    update_through_intersection(other) {
        this.indices = intersection(this.indices, other.indices);
        // TODO: think through and fix any logic below
        this.selected_glyphs = union(other.selected_glyphs, this.selected_glyphs);
        this.line_indices = union(other.line_indices, this.line_indices);
        this.view = other.view;
        this.multiline_indices = merge(other.multiline_indices, this.multiline_indices);
    }
    update_through_subtraction(other) {
        this.indices = difference(this.indices, other.indices);
        // TODO: think through and fix any logic below
        this.selected_glyphs = union(other.selected_glyphs, this.selected_glyphs);
        this.line_indices = union(other.line_indices, this.line_indices);
        this.view = other.view;
        this.multiline_indices = merge(other.multiline_indices, this.multiline_indices);
    }
}
_a = Selection;
Selection.__name__ = "Selection";
(() => {
    _a.define(({ Int, Array, Dict }) => ({
        indices: [Array(Int), []],
        line_indices: [Array(Int), []],
        multiline_indices: [Dict(Array(Int)), {}],
    }));
    _a.internal(({ Int, Array, AnyRef, Struct, Nullable }) => ({
        selected_glyphs: [Array(AnyRef()), []],
        view: [Nullable(AnyRef()), null],
        // Used internally to support hover tool for now. Python API TBD
        image_indices: [Array(Struct({ index: Int, dim1: Int, dim2: Int, flat_index: Int })), []],
    }));
})();
//# sourceMappingURL=selection.js.map