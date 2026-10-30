# iOS → HarmonyOS interaction mapping

| Native evidence | Target candidate | Preserve |
|---|---|---|
| Button action / UIAction / target-selector | onClick + business event | Enabled guard, ownership, parameters, async result, failure/cancel and repeat taps |
| onTapGesture / UITapGestureRecognizer | TapGesture or onClick | Count, coordinate space, competing gestures and actual hit area |
| onLongPressGesture / UILongPressGestureRecognizer | LongPressGesture | Minimum duration, movement tolerance, begin/end/cancel and simultaneous recognition |
| DragGesture / UIPanGestureRecognizer | PanGesture | Start/update/end/cancel, translation vs absolute position, threshold, coordinate space and gesture arbitration |
| MagnifyGesture / UIRotationGestureRecognizer / UIPinchGestureRecognizer | PinchGesture / RotationGesture candidate | Accumulated state, reset, focal point and cancellation |
| FocusState / UIKit first responder and delegates | Focus management + input callbacks | Requested vs actual focus, keyboard, submit and validation timing |
| Binding / onChange / delegate callbacks | V2 state + events / monitors | Source of truth, change ordering, avoiding feedback loops and async races |
| task / task(id:) / onAppear / onDisappear / UIViewController lifecycle | Target lifecycle + owned cancellable work | Visibility is not object destruction; preserve cancellation, re-entry, subscriptions and resource release |
| NavigationLink / path mutation / push / present / segue | Navigation / modal implementation | Trigger, destination, parameters, results, pop/dismiss, guards and deep-link entry |

## Gesture and lifecycle constraints

Do not equate touch coordinates, pressure, gesture phase or timestamps by field name. Preserve which events source code actually uses and verify the target API/units. SwiftUI highPriorityGesture/simultaneousGesture and UIKit recognizer delegates can change conflict resolution. A visually matching overlay can still block the underlying controls; apply original P-17 checks.

UI work must follow the source's actor/thread ownership and target UI lifecycle. Retain cancellation and generation checks for stale requests. Never replace a guarded asynchronous operation with immediate successful state mutation. Source observers/tasks and target listeners/timers must have matching lifetime owners.

Use arkts-animation-migrate for animation timing/interruptibility and arkts-navigation-builder for target routing. Mapping candidates do not establish source runtime observations or target behavior verification.
