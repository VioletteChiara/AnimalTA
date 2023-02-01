var _a;
import { MercatorTileSource } from "./mercator_tile_source";
export class BBoxTileSource extends MercatorTileSource {
    constructor(attrs) {
        super(attrs);
    }
    get_image_url(x, y, z) {
        const image_url = this.string_lookup_replace(this.url, this.extra_url_vars);
        let xmax, xmin, ymax, ymin;
        if (this.use_latlon)
            [xmin, ymin, xmax, ymax] = this.get_tile_geographic_bounds(x, y, z);
        else
            [xmin, ymin, xmax, ymax] = this.get_tile_meter_bounds(x, y, z);
        return image_url
            .replace("{XMIN}", xmin.toString())
            .replace("{YMIN}", ymin.toString())
            .replace("{XMAX}", xmax.toString())
            .replace("{YMAX}", ymax.toString());
    }
}
_a = BBoxTileSource;
BBoxTileSource.__name__ = "BBoxTileSource";
(() => {
    _a.define(({ Boolean }) => ({
        use_latlon: [Boolean, false],
    }));
})();
//# sourceMappingURL=bbox_tile_source.js.map