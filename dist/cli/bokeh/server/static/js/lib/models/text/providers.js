import { Signal0 } from "../../core/signaling";
import { load_module } from "../../core/util/modules";
export class MathJaxProvider {
    constructor() {
        this.ready = new Signal0(this, "ready");
        this.status = "not_started";
    }
}
MathJaxProvider.__name__ = "MathJaxProvider";
export class NoProvider extends MathJaxProvider {
    get MathJax() {
        return null;
    }
    async fetch() {
        this.status = "failed";
    }
}
NoProvider.__name__ = "NoProvider";
export class CDNProvider extends MathJaxProvider {
    get MathJax() {
        return typeof MathJax !== "undefined" ? MathJax : null;
    }
    async fetch() {
        const script = document.createElement("script");
        script.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js";
        script.onload = () => {
            this.status = "loaded";
            this.ready.emit();
        };
        script.onerror = () => {
            this.status = "failed";
        };
        this.status = "loading";
        document.head.appendChild(script);
    }
}
CDNProvider.__name__ = "CDNProvider";
export class BundleProvider extends MathJaxProvider {
    get MathJax() {
        return this._mathjax;
    }
    async fetch() {
        this.status = "loading";
        try {
            const mathjax = await load_module(import("./mathjax"));
            this._mathjax = mathjax;
            this.status = "loaded";
            this.ready.emit();
        }
        catch (error) {
            this.status = "failed";
        }
    }
}
BundleProvider.__name__ = "BundleProvider";
export const default_provider = new BundleProvider();
//# sourceMappingURL=providers.js.map