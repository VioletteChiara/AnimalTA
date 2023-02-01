import { AngleUnits } from "../enums";
export declare function angle_norm(angle: number): number;
export declare function angle_dist(lhs: number, rhs: number): number;
export declare function angle_between(mid: number, lhs: number, rhs: number, anticlock?: boolean): boolean;
export declare function random(): number;
export declare function randomIn(min: number, max?: number): number;
export declare function atan2(start: [number, number], end: [number, number]): number;
export declare function radians(degrees: number): number;
export declare function degrees(radians: number): number;
export declare function resolve_angle(angle: number, units: AngleUnits): number;
export declare function to_radians_coeff(units: AngleUnits): number;
export declare function rnorm(mu: number, sigma: number): number;
export declare function clamp(val: number, min: number, max: number): number;
export declare function log(x: number, base?: number): number;
export declare const float32_epsilon = 1.1920928955078125e-7;
//# sourceMappingURL=math.d.ts.map