export class AssertionError extends Error {
}
AssertionError.__name__ = "AssertionError";
export function assert(condition, message) {
    if (condition === true || (condition !== false && condition()))
        return;
    throw new AssertionError(message ?? "Assertion failed");
}
export function unreachable() {
    throw new Error("unreachable code");
}
//# sourceMappingURL=assert.js.map