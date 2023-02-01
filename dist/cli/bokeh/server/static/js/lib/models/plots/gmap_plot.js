var _a, _b, _c;
import { Plot } from "./plot";
import { Model } from "../../model";
import { Range1d } from "../ranges/range1d";
import { GMapPlotView } from "./gmap_plot_canvas";
export { GMapPlotView };
export class MapOptions extends Model {
    constructor(attrs) {
        super(attrs);
    }
}
_a = MapOptions;
MapOptions.__name__ = "MapOptions";
(() => {
    _a.define(({ Int, Number }) => ({
        lat: [Number],
        lng: [Number],
        zoom: [Int, 12],
    }));
})();
export class GMapOptions extends MapOptions {
    constructor(attrs) {
        super(attrs);
    }
}
_b = GMapOptions;
GMapOptions.__name__ = "GMapOptions";
(() => {
    _b.define(({ Boolean, Int, String }) => ({
        map_type: [String, "roadmap"],
        scale_control: [Boolean, false],
        styles: [String],
        tilt: [Int, 45],
    }));
})();
export class GMapPlot extends Plot {
    constructor(attrs) {
        super(attrs);
        this.use_map = true;
    }
}
_c = GMapPlot;
GMapPlot.__name__ = "GMapPlot";
(() => {
    _c.prototype.default_view = GMapPlotView;
    // This seems to be necessary so that everything can initialize.
    // Feels very clumsy, but I'm not sure how the properties system wants
    // to handle something like this situation.
    _c.define(({ String, Ref }) => ({
        map_options: [Ref(GMapOptions)],
        api_key: [String],
        api_version: [String, "3.43"],
    }));
    _c.override({
        x_range: () => new Range1d(),
        y_range: () => new Range1d(),
    });
})();
//# sourceMappingURL=gmap_plot.js.map