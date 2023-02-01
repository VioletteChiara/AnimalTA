var _a;
import { Model } from "../../model";
import { CoordinateTransform } from "../expressions/coordinate_transform";
export class LayoutProvider extends Model {
    constructor(attrs) {
        super(attrs);
    }
    get node_coordinates() {
        return new NodeCoordinates({ layout: this });
    }
    get edge_coordinates() {
        return new EdgeCoordinates({ layout: this });
    }
}
LayoutProvider.__name__ = "LayoutProvider";
export class GraphCoordinates extends CoordinateTransform {
    constructor(attrs) {
        super(attrs);
    }
}
_a = GraphCoordinates;
GraphCoordinates.__name__ = "GraphCoordinates";
(() => {
    _a.define(({ Ref }) => ({
        layout: [Ref(LayoutProvider)],
    }));
})();
export class NodeCoordinates extends GraphCoordinates {
    constructor(attrs) {
        super(attrs);
    }
    _v_compute(source) {
        const [x, y] = this.layout.get_node_coordinates(source);
        return { x, y };
    }
}
NodeCoordinates.__name__ = "NodeCoordinates";
export class EdgeCoordinates extends GraphCoordinates {
    constructor(attrs) {
        super(attrs);
    }
    _v_compute(source) {
        const [x, y] = this.layout.get_edge_coordinates(source);
        return { x, y };
    }
}
EdgeCoordinates.__name__ = "EdgeCoordinates";
//# sourceMappingURL=layout_provider.js.map