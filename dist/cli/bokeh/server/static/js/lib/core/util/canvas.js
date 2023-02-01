import { SVGRenderingContext2D } from "./svg";
import { BBox } from "./bbox";
import { div, canvas } from "../dom";
function fixup_line_dash(ctx) {
    if (typeof ctx.lineDash === "undefined") {
        Object.defineProperty(ctx, "lineDash", {
            get: () => ctx.getLineDash(),
            set: (segments) => ctx.setLineDash(segments),
        });
    }
}
function fixup_image_smoothing(ctx) {
    ctx.setImageSmoothingEnabled = (value) => {
        ctx.imageSmoothingEnabled = value;
        ctx.mozImageSmoothingEnabled = value;
        ctx.oImageSmoothingEnabled = value;
        ctx.webkitImageSmoothingEnabled = value;
        ctx.msImageSmoothingEnabled = value;
    };
    ctx.getImageSmoothingEnabled = () => {
        const val = ctx.imageSmoothingEnabled;
        return val != null ? val : true;
    };
}
function fixup_ellipse(ctx) {
    // implementing the ctx.ellipse function with bezier curves
    // we don't implement the startAngle, endAngle and anticlockwise arguments.
    function ellipse_bezier(x, y, radiusX, radiusY, rotation, _startAngle, _endAngle, anticlockwise = false) {
        const c = 0.551784; // see http://www.tinaja.com/glib/ellipse4.pdf
        ctx.translate(x, y);
        ctx.rotate(rotation);
        let rx = radiusX;
        let ry = radiusY;
        if (anticlockwise) {
            rx = -radiusX;
            ry = -radiusY;
        }
        ctx.moveTo(-rx, 0); // start point of first curve
        ctx.bezierCurveTo(-rx, ry * c, -rx * c, ry, 0, ry);
        ctx.bezierCurveTo(rx * c, ry, rx, ry * c, rx, 0);
        ctx.bezierCurveTo(rx, -ry * c, rx * c, -ry, 0, -ry);
        ctx.bezierCurveTo(-rx * c, -ry, -rx, -ry * c, -rx, 0);
        ctx.rotate(-rotation);
        ctx.translate(-x, -y);
    }
    if (!ctx.ellipse)
        ctx.ellipse = ellipse_bezier;
}
function fixup_ctx(ctx) {
    fixup_line_dash(ctx);
    fixup_image_smoothing(ctx);
    fixup_ellipse(ctx);
}
const style = {
    position: "absolute",
    top: "0",
    left: "0",
    width: "100%",
    height: "100%",
};
export class CanvasLayer {
    constructor(backend, hidpi) {
        this.backend = backend;
        this.hidpi = hidpi;
        this.pixel_ratio = 1;
        this.bbox = new BBox();
        switch (backend) {
            case "webgl":
            case "canvas": {
                this._el = this._canvas = canvas({ style });
                const ctx = this.canvas.getContext("2d");
                if (ctx == null)
                    throw new Error("unable to obtain 2D rendering context");
                this._ctx = ctx;
                if (hidpi) {
                    this.pixel_ratio = devicePixelRatio;
                }
                break;
            }
            case "svg": {
                const ctx = new SVGRenderingContext2D();
                this._ctx = ctx;
                this._canvas = ctx.get_svg();
                this._el = div({ style }, this._canvas);
                break;
            }
        }
        this._ctx.layer = this;
        fixup_ctx(this._ctx);
    }
    get canvas() {
        return this._canvas;
    }
    get ctx() {
        return this._ctx;
    }
    get el() {
        return this._el;
    }
    resize(width, height) {
        this.bbox = new BBox({ left: 0, top: 0, width, height });
        const target = this._ctx instanceof SVGRenderingContext2D ? this._ctx : this.canvas;
        target.width = width * this.pixel_ratio;
        target.height = height * this.pixel_ratio;
    }
    undo_transform(fn) {
        const { ctx } = this;
        if (typeof ctx.getTransform === "undefined") {
            // XXX: remove this when IE/legacy is dropped
            fn(ctx);
        }
        else {
            const current_transform = ctx.getTransform();
            ctx.setTransform(this._base_transform);
            try {
                fn(ctx);
            }
            finally {
                ctx.setTransform(current_transform);
            }
        }
    }
    prepare() {
        const { ctx, hidpi, pixel_ratio } = this;
        ctx.save();
        if (hidpi) {
            ctx.scale(pixel_ratio, pixel_ratio);
            ctx.translate(0.5, 0.5);
        }
        if (typeof ctx.getTransform !== "undefined") { // XXX: remove this line when IE/legacy is dropped
            this._base_transform = ctx.getTransform();
        }
        this.clear();
    }
    clear() {
        const { x, y, width, height } = this.bbox;
        this.ctx.clearRect(x, y, width, height);
    }
    finish() {
        this.ctx.restore();
    }
    to_blob() {
        const { _canvas } = this;
        if (_canvas instanceof HTMLCanvasElement) {
            if (_canvas.msToBlob != null) {
                return Promise.resolve(_canvas.msToBlob());
            }
            else {
                return new Promise((resolve, reject) => {
                    _canvas.toBlob((blob) => blob != null ? resolve(blob) : reject(), "image/png");
                });
            }
        }
        else {
            const ctx = this._ctx;
            const svg = ctx.get_serialized_svg(true);
            const blob = new Blob([svg], { type: "image/svg+xml" });
            return Promise.resolve(blob);
        }
    }
}
CanvasLayer.__name__ = "CanvasLayer";
//# sourceMappingURL=canvas.js.map