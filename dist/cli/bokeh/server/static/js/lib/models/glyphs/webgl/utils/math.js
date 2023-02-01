// Greatest Common Divisor of 2+ integers using Euclid's algorithm.
function gcd2(a, b) {
    let higher;
    let lower;
    if (a > b) {
        higher = a;
        lower = b;
    }
    else {
        higher = b;
        lower = a;
    }
    let divisor = higher % lower;
    while (divisor != 0) {
        higher = lower;
        lower = divisor;
        divisor = higher % lower;
    }
    return lower;
}
export function gcd(values) {
    let ret = values[0];
    for (let i = 1; i < values.length; i++)
        ret = gcd2(ret, values[i]);
    return ret;
}
// From regl
export function is_pow_2(v) {
    return !(v & (v - 1)) && (!!v);
}
//# sourceMappingURL=math.js.map