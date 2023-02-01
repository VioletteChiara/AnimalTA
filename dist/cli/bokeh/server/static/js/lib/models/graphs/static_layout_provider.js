var _a;
import { LayoutProvider } from "./layout_provider";
export class StaticLayoutProvider extends LayoutProvider {
    constructor(attrs) {
        super(attrs);
    }
    get_node_coordinates(node_source) {
        const index = node_source.data.index ?? [];
        const n = index.length;
        const xs = new Float64Array(n);
        const ys = new Float64Array(n);
        for (let i = 0; i < n; i++) {
            const point = this.graph_layout[index[i]];
            const [x, y] = point ?? [NaN, NaN];
            xs[i] = x;
            ys[i] = y;
        }
        return [xs, ys];
    }
    get_edge_coordinates(edge_source) {
        const starts = edge_source.data.start ?? [];
        const ends = edge_source.data.end ?? [];
        const n = Math.min(starts.length, ends.length);
        const xs = [];
        const ys = [];
        const has_paths = edge_source.data.xs != null && edge_source.data.ys != null;
        for (let i = 0; i < n; i++) {
            const in_layout = this.graph_layout[starts[i]] != null && this.graph_layout[ends[i]] != null;
            if (has_paths && in_layout) {
                xs.push(edge_source.data.xs[i]);
                ys.push(edge_source.data.ys[i]);
            }
            else {
                let start, end;
                if (in_layout) {
                    start = this.graph_layout[starts[i]];
                    end = this.graph_layout[ends[i]];
                }
                else {
                    start = [NaN, NaN];
                    end = [NaN, NaN];
                }
                xs.push([start[0], end[0]]);
                ys.push([start[1], end[1]]);
            }
        }
        return [xs, ys];
    }
}
_a = StaticLayoutProvider;
StaticLayoutProvider.__name__ = "StaticLayoutProvider";
(() => {
    _a.define(({ Number, Tuple, Dict }) => ({
        graph_layout: [Dict(Tuple(Number, Number)), {}],
    }));
})();
//# sourceMappingURL=static_layout_provider.js.map