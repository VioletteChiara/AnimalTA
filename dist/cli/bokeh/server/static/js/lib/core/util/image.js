import { logger } from "../logging";
export async function load_image(url, options) {
    return new ImageLoader(url, options).promise;
}
export class ImageLoader {
    constructor(url, config = {}) {
        this._image = new Image();
        this._finished = false;
        const { attempts = 1, timeout = 1 } = config;
        this.promise = new Promise((resolve, _reject) => {
            this._image.crossOrigin = "anonymous";
            let retries = 0;
            this._image.onerror = () => {
                if (++retries == attempts) {
                    const message = `unable to load ${url} image after ${attempts} attempts`;
                    logger.warn(message);
                    if (this._image.crossOrigin != null) {
                        logger.warn(`attempting to load ${url} without a cross origin policy`);
                        this._image.crossOrigin = null;
                        retries = 0;
                    }
                    else {
                        if (config.failed != null)
                            config.failed();
                        return; // XXX reject(new Error(message))
                    }
                }
                setTimeout(() => this._image.src = url, timeout);
            };
            this._image.onload = () => {
                this._finished = true;
                if (config.loaded != null)
                    config.loaded(this._image);
                resolve(this._image);
            };
            this._image.src = url;
        });
    }
    get finished() {
        return this._finished;
    }
    get image() {
        if (this._finished)
            return this._image;
        else
            throw new Error("not loaded yet");
    }
}
ImageLoader.__name__ = "ImageLoader";
//# sourceMappingURL=image.js.map