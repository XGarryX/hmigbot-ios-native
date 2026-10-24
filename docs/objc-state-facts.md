# Objective-C state facts

The native `facts` producer inventories Objective-C property and ivar declarations
in `.h`, `.m`, and `.mm` files. It preserves the declaring class, source span,
declared type, property attributes, reference ownership tokens, and known trailing
annotations. These facts remain `resolution=token_signal`; they are neither a
Clang binding nor proof of runtime behavior.

`objc_ivar` means an explicit instance-variable declaration. `objc_property` means
a property declaration, which may be computed or dynamically implemented. A
header alone does not prove synthesized storage. Explicit `@synthesize` aliases
and conservative automatic-synthesis candidates are distinguished from unresolved
storage. Class properties, named categories, `@dynamic`, and custom accessors do
not receive an invented backing ivar.

`initializer` describes allocation zero initialization only when instance storage
has an identified declaration or lexical synthesis candidate. `initializer_basis`
and `storage_binding` retain that limitation. Unknown typedefs, aggregate values,
or unresolved storage keep a null initializer. Explicit assignments in `init`,
UIKit lifecycle methods, lazy getters, and other methods stay in `assignments`,
with their source path, line, selector, phase, and `control_flow=lexical_only`.
An assignment's presence does not prove its branch executed or its value was the
value observed after initialization. External-object writes remain ordinary write
facts rather than guessed receiver bindings.

For `state_ownership`, each reviewed `states` item is constructed from the current
state fact's `fact_id`, `owner`, and **all fields of `fact.value`**. The existing
checker compares the complete value, including ownership, backing/storage basis,
and assignment evidence. Dropping a real state or changing these fields remains
an error. The shorter Swift example containing only storage/type/initializer is
not a reason to discard additional Objective-C evidence.

The bounded parser recognizes ordinary pointer/scalar/generic declarations,
standard block properties, standard property attributes and accessors, and
balanced `API_AVAILABLE` / `UI_APPEARANCE_SELECTOR` suffixes. Unsupported syntax
produces `IOS.OBJC_STATE_UNRESOLVED`; it cannot silently turn into a field name or
an empty successful inventory. Unknown macros require expanded compiler evidence
or further parser support. Neither a fallback parser nor a new state fact marks
an unknown SDK implementation or a source gate as passed.

C character literals currently fail closed for that file's state inference, with
an explicit unresolved finding. This prevents braces and quotes inside a character
literal from being interpreted as method boundaries or complete assignments.
Ordinary pre-existing source facts remain present; a missing state list accompanied
by this finding is not evidence that the file owns no state.

After upgrading, regenerate facts and obligations through the installed producer,
review affected semantics and AC mappings, and rerun `spec-check` and
`source-check --harness`. The state extractor is included in the frozen tool
revision. Existing source, plan and receipt controls continue to apply; tool tests
do not establish application compilation or device/behavior verification.
