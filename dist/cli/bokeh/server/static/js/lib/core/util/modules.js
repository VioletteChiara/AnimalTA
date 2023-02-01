function is_ModuleError(error) {
    return error instanceof Error && "code" in error;
}
/** T is of import("some/module/path") type */
export async function load_module(module) {
    try {
        return await module;
    }
    catch (e) {
        // XXX: this exposes the underyling module system and hinders
        // interoperability with other module systems and bundlers
        if (is_ModuleError(e) && e.code === "MODULE_NOT_FOUND")
            return null;
        else
            throw e;
    }
}
//# sourceMappingURL=modules.js.map