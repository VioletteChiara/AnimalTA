export declare type Image = HTMLImageElement;
export declare type ImageHandlers = {
    loaded?: (image: Image) => void;
    failed?: () => void;
};
export declare type LoaderOptions = {
    attempts?: number;
    timeout?: number;
};
export declare function load_image(url: string, options?: LoaderOptions): Promise<Image>;
export declare class ImageLoader {
    private _image;
    promise: Promise<Image>;
    constructor(url: string, config?: ImageHandlers & LoaderOptions);
    private _finished;
    get finished(): boolean;
    get image(): Image;
}
//# sourceMappingURL=image.d.ts.map