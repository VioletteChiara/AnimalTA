const { PI } = Math;
export function angle_norm(angle) {
    if (angle == 0) {
        return 0;
    }
    while (angle <= 0) {
        angle += 2 * PI;
    }
    while (angle > 2 * PI) {
        angle -= 2 * PI;
    }
    return angle;
}
export function angle_dist(lhs, rhs) {
    return angle_norm(lhs - rhs);
}
export function angle_between(mid, lhs, rhs, anticlock = false) {
    const d = angle_dist(lhs, rhs);
    if (d == 0)
        return false;
    if (d == 2 * PI)
        return true;
    const norm_mid = angle_norm(mid);
    const cond = angle_dist(lhs, norm_mid) <= d && angle_dist(norm_mid, rhs) <= d;
    return !anticlock ? cond : !cond;
}
export function random() {
    return Math.random();
}
export function randomIn(min, max) {
    if (max == null) {
        max = min;
        min = 0;
    }
    return min + Math.floor(Math.random() * (max - min + 1));
}
export function atan2(start, end) {
    /*
     * Calculate the angle between a line containing start and end points (composed
     * of [x, y] arrays) and the positive x-axis.
     */
    return Math.atan2(end[1] - start[1], end[0] - start[0]);
}
export function radians(degrees) {
    return degrees * (PI / 180);
}
export function degrees(radians) {
    return radians / (PI / 180);
}
export function resolve_angle(angle, units) {
    /** Convert CCW angle with units to CW radians (canvas). */
    return -to_radians_coeff(units) * angle;
}
export function to_radians_coeff(units) {
    switch (units) {
        case "deg": return PI / 180;
        case "rad": return 1;
        case "grad": return PI / 200;
        case "turn": return 2 * PI;
    }
}
// http://www2.econ.osaka-u.ac.jp/~tanizaki/class/2013/econome3/13.pdf (Page 432)
export function rnorm(mu, sigma) {
    // Generate a random normal with a mean of 0 and a sigma of 1
    let r1;
    let r2;
    while (true) {
        r1 = random();
        r2 = random();
        r2 = (2 * r2 - 1) * Math.sqrt(2 * (1 / Math.E));
        if (-4 * r1 * r1 * Math.log(r1) >= r2 * r2)
            break;
    }
    let rn = r2 / r1;
    // Transform the standard normal to meet the characteristics that we want (mu, sigma)
    rn = mu + sigma * rn;
    return rn;
}
export function clamp(val, min, max) {
    return val < min ? min : (val > max ? max : val);
}
export function log(x, base = Math.E) {
    return Math.log(x) / Math.log(base);
}
export const float32_epsilon = 1.1920928955078125e-7; // IEEE-754
//# sourceMappingURL=math.js.map