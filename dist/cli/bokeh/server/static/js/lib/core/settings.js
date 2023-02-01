export class Settings {
    constructor() {
        this._dev = false;
        this._wireframe = false;
    }
    set dev(dev) {
        this._dev = dev;
    }
    get dev() {
        return this._dev;
    }
    set wireframe(wireframe) {
        this._wireframe = wireframe;
    }
    get wireframe() {
        return this._wireframe;
    }
}
Settings.__name__ = "Settings";
export const settings = new Settings();
//# sourceMappingURL=settings.js.map