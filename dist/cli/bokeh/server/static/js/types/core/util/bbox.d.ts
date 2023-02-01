import { Arrayable, ScreenArray, Rect, Box, Interval, Size } from "../types";
import { equals, Equatable, Comparator } from "./eq";
import { Rect as GraphicsRect } from "./affine";
export declare function empty(): Rect;
export declare function positive_x(): Rect;
export declare function positive_y(): Rect;
export declare function union(a: Rect, b: Rect): Rect;
export declare type HorizontalPosition = {
    left: number;
    width: number;
} | {
    width: number;
    right: number;
} | {
    left: number;
    right: number;
} | {
    hcenter: number;
    width: number;
};
export declare type VerticalPosition = {
    top: number;
    height: number;
} | {
    height: number;
    bottom: number;
} | {
    top: number;
    bottom: number;
} | {
    vcenter: number;
    height: number;
};
export declare type Position = HorizontalPosition & VerticalPosition;
export declare type CoordinateMapper = {
    compute: (v: number) => number;
    v_compute: (vv: Arrayable<number>) => ScreenArray;
};
export declare class BBox implements Rect, Equatable {
    readonly x0: number;
    readonly y0: number;
    readonly x1: number;
    readonly y1: number;
    constructor(box?: Rect | Box | Position);
    static from_rect({ left, right, top, bottom }: {
        left: number;
        right: number;
        top: number;
        bottom: number;
    }): BBox;
    equals(that: Rect): boolean;
    [equals](that: this, cmp: Comparator): boolean;
    toString(): string;
    get left(): number;
    get top(): number;
    get right(): number;
    get bottom(): number;
    get p0(): [number, number];
    get p1(): [number, number];
    get x(): number;
    get y(): number;
    get width(): number;
    get height(): number;
    get size(): Size;
    get rect(): GraphicsRect;
    get box(): Box;
    get h_range(): Interval;
    get v_range(): Interval;
    get ranges(): [Interval, Interval];
    get aspect(): number;
    get hcenter(): number;
    get vcenter(): number;
    get area(): number;
    relative(): BBox;
    translate(tx: number, ty: number): BBox;
    relativize(x: number, y: number): [number, number];
    contains(x: number, y: number): boolean;
    clip(x: number, y: number): [number, number];
    grow_by(size: number): BBox;
    shrink_by(size: number): BBox;
    union(that: Rect): BBox;
    intersection(that: Rect): BBox | null;
    intersects(that: Rect): boolean;
    get xview(): CoordinateMapper;
    get yview(): CoordinateMapper;
}
//# sourceMappingURL=bbox.d.ts.map