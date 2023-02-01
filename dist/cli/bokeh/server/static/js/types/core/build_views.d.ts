import { HasProps } from "./has_props";
import { View, ViewOf } from "./view";
export declare type ViewStorage<T extends HasProps> = Map<T, ViewOf<T>>;
export declare type Options<T extends View> = {
    parent: T["parent"] | null;
};
export declare function build_view<T extends HasProps>(model: T, options?: Options<ViewOf<T>>, cls?: (model: T) => T["default_view"]): Promise<ViewOf<T>>;
export declare function build_views<T extends HasProps>(view_storage: ViewStorage<T>, models: T[], options?: Options<ViewOf<T>>, cls?: (model: T) => T["default_view"]): Promise<ViewOf<T>[]>;
export declare function remove_views(view_storage: ViewStorage<HasProps>): void;
//# sourceMappingURL=build_views.d.ts.map