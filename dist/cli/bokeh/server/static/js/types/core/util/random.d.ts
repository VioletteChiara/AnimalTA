export declare class Random {
    private seed;
    constructor(seed: number);
    integer(): number;
    float(): number;
    floats(n: number, a?: number, b?: number): number[];
    choices<T>(n: number, items: ArrayLike<T>): T[];
}
export declare const random: Random;
//# sourceMappingURL=random.d.ts.map