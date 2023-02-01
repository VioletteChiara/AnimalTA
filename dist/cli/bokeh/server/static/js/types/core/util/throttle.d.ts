/**
 * Returns a function, that, when invoked, will only be triggered at
 * most once during a given interval of time and no more frequently
 * than the animation frame rate allows it.
 *
 * @param func [function] the function to throttle
 * @param wait [number] time in milliseconds to use for window
 * @return [function] throttled function
 */
export declare function throttle(func: () => void, wait: number): () => Promise<void>;
//# sourceMappingURL=throttle.d.ts.map