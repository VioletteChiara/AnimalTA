export declare type ThrottleOptions = {
    leading?: boolean;
    trailing?: boolean;
};
export declare function throttle<T>(func: () => T, wait: number, options?: ThrottleOptions): (this: any) => T;
export declare function once<T>(func: () => T): () => T;
//# sourceMappingURL=callback.d.ts.map