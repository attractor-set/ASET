# RC12 to Seed Resolution Core

This is an intentional breaking semantic narrowing.

The active Seed no longer defines the complete execution, verification, federation and lifecycle protocol. It defines only an exact resolution cycle whose semantic state starts as `UNKNOWN`, may be explicitly escalated while remaining `UNKNOWN`, and terminates as `ACCEPT` or `DENY`.

`UNKNOWN` is always operationally blocked and is never silently rewritten as `DENY`. Context ancestry and federation membership do not create authority; every escalation requires an exact grant.

The former rc11/rc12 concepts remain historical evidence and are migration sources for separate Context, Federation, Core, Monade and implementation extensions.
