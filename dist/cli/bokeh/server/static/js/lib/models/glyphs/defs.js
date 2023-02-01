const SQ3 = Math.sqrt(3);
const SQ5 = Math.sqrt(5);
const c36 = (SQ5 + 1) / 4;
const s36 = Math.sqrt((5 - SQ5) / 8);
const c72 = (SQ5 - 1) / 4;
const s72 = Math.sqrt((5 + SQ5) / 8);
function _one_line(ctx, r) {
    ctx.moveTo(-r, 0);
    ctx.lineTo(r, 0);
}
function _one_x(ctx, r) {
    ctx.rotate(Math.PI / 4);
    _one_cross(ctx, r);
    ctx.rotate(-Math.PI / 4);
}
function _one_y(ctx, r) {
    const h = r * SQ3;
    const a = h / 3;
    ctx.moveTo(-h / 2, -a);
    ctx.lineTo(0, 0);
    ctx.lineTo(h / 2, -a);
    ctx.lineTo(0, 0);
    ctx.lineTo(0, r);
}
function _one_cross(ctx, r) {
    ctx.moveTo(0, r);
    ctx.lineTo(0, -r);
    ctx.moveTo(-r, 0);
    ctx.lineTo(r, 0);
}
function _one_dot(ctx, r) {
    ctx.beginPath();
    ctx.arc(0, 0, r / 4, 0, 2 * Math.PI, false);
    ctx.closePath();
}
function _one_diamond(ctx, r) {
    ctx.moveTo(0, r);
    ctx.lineTo(r / 1.5, 0);
    ctx.lineTo(0, -r);
    ctx.lineTo(-r / 1.5, 0);
    ctx.closePath();
}
function _one_hex(ctx, r) {
    const r2 = r / 2;
    const h = SQ3 * r2;
    ctx.moveTo(r, 0);
    ctx.lineTo(r2, -h);
    ctx.lineTo(-r2, -h);
    ctx.lineTo(-r, 0);
    ctx.lineTo(-r2, h);
    ctx.lineTo(r2, h);
    ctx.closePath();
}
function _one_star(ctx, r) {
    const a = Math.sqrt(5 - 2 * SQ5) * r;
    ctx.moveTo(0, -r);
    ctx.lineTo(a * c72, -r + a * s72);
    ctx.lineTo(a * (1 + c72), -r + a * s72);
    ctx.lineTo(a * (1 + c72 - c36), -r + a * (s72 + s36));
    ctx.lineTo(a * (1 + 2 * c72 - c36), -r + a * (2 * s72 + s36));
    ctx.lineTo(0, -r + a * 2 * s72);
    ctx.lineTo(-a * (1 + 2 * c72 - c36), -r + a * (2 * s72 + s36));
    ctx.lineTo(-a * (1 + c72 - c36), -r + a * (s72 + s36));
    ctx.lineTo(-a * (1 + c72), -r + a * s72);
    ctx.lineTo(-a * c72, -r + a * s72);
    ctx.closePath();
}
function _one_tri(ctx, r) {
    const h = r * SQ3;
    const a = h / 3;
    ctx.moveTo(-r, a);
    ctx.lineTo(r, a);
    ctx.lineTo(0, a - h);
    ctx.closePath();
}
function asterisk(ctx, i, r, visuals) {
    _one_cross(ctx, r);
    _one_x(ctx, r);
    visuals.line.apply(ctx, i);
}
function circle(ctx, i, r, visuals) {
    ctx.arc(0, 0, r, 0, 2 * Math.PI, false);
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    visuals.line.apply(ctx, i);
}
function circle_cross(ctx, i, r, visuals) {
    ctx.arc(0, 0, r, 0, 2 * Math.PI, false);
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    if (visuals.line.doit) {
        visuals.line.set_vectorize(ctx, i);
        _one_cross(ctx, r);
        ctx.stroke();
    }
}
function circle_dot(ctx, i, r, visuals) {
    circle(ctx, i, r, visuals);
    dot(ctx, i, r, visuals);
}
function circle_y(ctx, i, r, visuals) {
    ctx.arc(0, 0, r, 0, 2 * Math.PI, false);
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    if (visuals.line.doit) {
        visuals.line.set_vectorize(ctx, i);
        _one_y(ctx, r);
        ctx.stroke();
    }
}
function circle_x(ctx, i, r, visuals) {
    ctx.arc(0, 0, r, 0, 2 * Math.PI, false);
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    if (visuals.line.doit) {
        visuals.line.set_vectorize(ctx, i);
        _one_x(ctx, r);
        ctx.stroke();
    }
}
function cross(ctx, i, r, visuals) {
    _one_cross(ctx, r);
    visuals.line.apply(ctx, i);
}
function diamond(ctx, i, r, visuals) {
    _one_diamond(ctx, r);
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    visuals.line.apply(ctx, i);
}
function diamond_cross(ctx, i, r, visuals) {
    _one_diamond(ctx, r);
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    if (visuals.line.doit) {
        visuals.line.set_vectorize(ctx, i);
        ctx.moveTo(0, r);
        ctx.lineTo(0, -r);
        ctx.moveTo(-r / 1.5, 0);
        ctx.lineTo(r / 1.5, 0);
        ctx.stroke();
    }
}
function diamond_dot(ctx, i, r, visuals) {
    diamond(ctx, i, r, visuals);
    dot(ctx, i, r, visuals);
}
function dot(ctx, i, r, visuals) {
    _one_dot(ctx, r);
    visuals.line.set_vectorize(ctx, i);
    ctx.fillStyle = ctx.strokeStyle; // NOTE: dots use line color for fill to match
    ctx.fill();
}
function hex(ctx, i, r, visuals) {
    _one_hex(ctx, r);
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    visuals.line.apply(ctx, i);
}
function hex_dot(ctx, i, r, visuals) {
    hex(ctx, i, r, visuals);
    dot(ctx, i, r, visuals);
}
function inverted_triangle(ctx, i, r, visuals) {
    ctx.rotate(Math.PI);
    _one_tri(ctx, r);
    ctx.rotate(-Math.PI);
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    visuals.line.apply(ctx, i);
}
function plus(ctx, i, r, visuals) {
    const a = 3 * r / 8;
    const b = r;
    const xs = [a, a, b, b, a, a, -a, -a, -b, -b, -a, -a];
    const ys = [b, a, a, -a, -a, -b, -b, -a, -a, a, a, b];
    ctx.beginPath();
    for (let j = 0; j < 12; j++) {
        ctx.lineTo(xs[j], ys[j]);
    }
    ctx.closePath();
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    visuals.line.apply(ctx, i);
}
function square(ctx, i, r, visuals) {
    const size = 2 * r;
    ctx.rect(-r, -r, size, size);
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    visuals.line.apply(ctx, i);
}
function square_pin(ctx, i, r, visuals) {
    const a = 3 * r / 8;
    ctx.moveTo(-r, -r);
    /* eslint-disable space-in-parens */
    ctx.quadraticCurveTo(0, -a, r, -r);
    ctx.quadraticCurveTo(a, 0, r, r);
    ctx.quadraticCurveTo(0, a, -r, r);
    ctx.quadraticCurveTo(-a, 0, -r, -r);
    /* eslint-ensable space-in-parens */
    ctx.closePath();
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    visuals.line.apply(ctx, i);
}
function square_cross(ctx, i, r, visuals) {
    const size = 2 * r;
    ctx.rect(-r, -r, size, size);
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    if (visuals.line.doit) {
        visuals.line.set_vectorize(ctx, i);
        _one_cross(ctx, r);
        ctx.stroke();
    }
}
function square_dot(ctx, i, r, visuals) {
    square(ctx, i, r, visuals);
    dot(ctx, i, r, visuals);
}
function square_x(ctx, i, r, visuals) {
    const size = 2 * r;
    ctx.rect(-r, -r, size, size);
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    if (visuals.line.doit) {
        visuals.line.set_vectorize(ctx, i);
        ctx.moveTo(-r, r);
        ctx.lineTo(r, -r);
        ctx.moveTo(-r, -r);
        ctx.lineTo(r, r);
        ctx.stroke();
    }
}
function star(ctx, i, r, visuals) {
    _one_star(ctx, r);
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    visuals.line.apply(ctx, i);
}
function star_dot(ctx, i, r, visuals) {
    star(ctx, i, r, visuals);
    dot(ctx, i, r, visuals);
}
function triangle(ctx, i, r, visuals) {
    _one_tri(ctx, r);
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    visuals.line.apply(ctx, i);
}
function triangle_dot(ctx, i, r, visuals) {
    triangle(ctx, i, r, visuals);
    dot(ctx, i, r, visuals);
}
function triangle_pin(ctx, i, r, visuals) {
    const h = r * SQ3;
    const a = h / 3;
    const b = 3 * a / 8;
    ctx.moveTo(-r, a);
    ctx.quadraticCurveTo(0, b, r, a);
    ctx.quadraticCurveTo(SQ3 * b / 2, b / 2, 0, a - h);
    ctx.quadraticCurveTo(-SQ3 * b / 2, b / 2, -r, a);
    ctx.closePath();
    visuals.fill.apply(ctx, i);
    visuals.hatch.apply(ctx, i);
    visuals.line.apply(ctx, i);
}
function dash(ctx, i, r, visuals) {
    _one_line(ctx, r);
    visuals.line.apply(ctx, i);
}
function x(ctx, i, r, visuals) {
    _one_x(ctx, r);
    visuals.line.apply(ctx, i);
}
function y(ctx, i, r, visuals) {
    _one_y(ctx, r);
    visuals.line.apply(ctx, i);
}
export const marker_funcs = {
    asterisk,
    circle,
    circle_cross,
    circle_dot,
    circle_y,
    circle_x,
    cross,
    diamond,
    diamond_dot,
    diamond_cross,
    dot,
    hex,
    hex_dot,
    inverted_triangle,
    plus,
    square,
    square_cross,
    square_dot,
    square_pin,
    square_x,
    star,
    star_dot,
    triangle,
    triangle_dot,
    triangle_pin,
    dash,
    x,
    y,
};
//# sourceMappingURL=defs.js.map