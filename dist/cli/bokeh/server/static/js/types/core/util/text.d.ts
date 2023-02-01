declare type char = string;
export declare type BoxMetrics = {
    width: number;
    height: number;
    ascent: number;
    descent: number;
};
export declare type FontMetrics = {
    height: number;
    ascent: number;
    descent: number;
    cap_height: number;
    x_height: number;
};
export declare function font_metrics(font: string): FontMetrics;
export declare function glyph_metrics(glyph: char, font: string): BoxMetrics;
export declare function parse_css_font_size(size: string): {
    value: number;
    unit: string;
} | null;
export {};
//# sourceMappingURL=text.d.ts.map