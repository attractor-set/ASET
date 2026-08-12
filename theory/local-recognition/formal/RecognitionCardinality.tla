---------------------- MODULE RecognitionCardinality ----------------------
EXTENDS FiniteSets

RecognitionStates == {"U", "A", "B"}
TwoValues == {"0", "1"}
ThreeValues == {"0", "1", "2"}

Terminal(s) == s \in {"A", "B"}
EffectPermitted(s) == s = "A"
Observables(s) ==
  [terminal |-> Terminal(s),
   effect_permitted |-> EffectPermitted(s)]

Faithful(f, codomain) ==
  /\ f \in [RecognitionStates -> codomain]
  /\ \A x \in RecognitionStates, y \in RecognitionStates :
       Observables(x) # Observables(y) => f[x] # f[y]

CanonicalThreeEncoding ==
  [s \in RecognitionStates |->
     CASE s = "U" -> "0"
       [] s = "A" -> "1"
       [] OTHER   -> "2"]

=============================================================================
