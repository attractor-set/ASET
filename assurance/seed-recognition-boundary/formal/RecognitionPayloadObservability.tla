---------------- MODULE RecognitionPayloadObservability ----------------
EXTENDS RecognitionOperationalCardinality

(***************************************************************************)
(* Payload observability for the canonical per-resolution normal form.     *)
(*                                                                         *)
(* This module deliberately separates:                                     *)
(*                                                                         *)
(*   1. effective state observation;                                       *)
(*   2. coarse action-kind capability;                                     *)
(*   3. retained terminal history;                                         *)
(*   4. parameterized submit capability;                                   *)
(*   5. exact canonical/Seed-state observation.                            *)
(*                                                                         *)
(* The witness universe is finite and intentionally non-degenerate:        *)
(*   - two recognized bindings;                                            *)
(*   - two previous values;                                                *)
(*   - one binding accepted by two authorities.                            *)
(*                                                                         *)
(* Therefore it can falsify unconditional claims that binding, previous,   *)
(* or terminal authority are always eliminable from exact state.           *)
(*                                                                         *)
(* It does NOT claim universal coordinate necessity in degenerate domains. *)
(* For example, authority is derivable when every recognized binding has   *)
(* exactly one recognized authority.                                       *)
(***************************************************************************)

BindingsWitness == {"B0", "B1"}
AuthoritiesWitness == {"A0", "A1"}
PreviousWitness == {"P0", "P1"}

NoBindingWitness == "NO_BINDING"
NoPreviousWitness == "NO_PREVIOUS"
NoAuthorityWitness == "NO_AUTHORITY"

WitnessRecognizedAuthorityBindings ==
  {<<"A0", "B0">>,
   <<"A1", "B0">>,
   <<"A0", "B1">>}

TerminalPhases ==
  {"ALLOW", "BLOCK", "INVALIDATED_ALLOW", "INVALIDATED_BLOCK"}

WitnessTerminalResolutions == {"ALLOW", "BLOCK"}

PayloadStateType ==
  [phase : OperationalPhases,
   binding : BindingsWitness \cup {NoBindingWitness},
   previous : PreviousWitness \cup {NoPreviousWitness},
   authority : AuthoritiesWitness \cup {NoAuthorityWitness}]

ValidPayloadState(s) ==
  CASE s.phase = "ABSENT" ->
         /\ s.binding = NoBindingWitness
         /\ s.previous = NoPreviousWitness
         /\ s.authority = NoAuthorityWitness
    [] s.phase = "PENDING" ->
         /\ s.binding \in BindingsWitness
         /\ s.previous \in PreviousWitness
         /\ s.authority = NoAuthorityWitness
    [] OTHER ->
         /\ s.phase \in TerminalPhases
         /\ s.binding \in BindingsWitness
         /\ s.previous \in PreviousWitness
         /\ s.authority \in AuthoritiesWitness
         /\ <<s.authority, s.binding>>
              \in WitnessRecognizedAuthorityBindings

ValidPayloadStates ==
  {s \in PayloadStateType : ValidPayloadState(s)}

EffectiveStateObservables(s) ==
  [effective |-> EffectiveValue(s.phase)]

CoarseCapabilityStateObservables(s) ==
  CapabilityObservables(s.phase)

RetainedHistoryStateObservables(s) ==
  HistoryObservables(s.phase)

PendingBindingKey(s) ==
  IF s.phase = "PENDING"
  THEN s.binding
  ELSE NoBindingWitness

ParameterizedCapabilityStateObservables(s) ==
  [history |-> RetainedHistoryStateObservables(s),
   pending_binding |-> PendingBindingKey(s)]

SubmitAuthorities(s) ==
  {a \in AuthoritiesWitness :
     <<a, s.binding>> \in WitnessRecognizedAuthorityBindings}

EnabledSubmitLabels(s) ==
  IF s.phase = "PENDING"
  THEN UNION
         {{<<s.binding, a, value>> : value \in WitnessTerminalResolutions} :
            a \in SubmitAuthorities(s)}
  ELSE {}

ExactStateObservables(s) == s

EffectiveStateObservationMap ==
  [s \in ValidPayloadStates |-> EffectiveStateObservables(s)]

CoarseCapabilityStateObservationMap ==
  [s \in ValidPayloadStates |-> CoarseCapabilityStateObservables(s)]

RetainedHistoryStateObservationMap ==
  [s \in ValidPayloadStates |-> RetainedHistoryStateObservables(s)]

ParameterizedCapabilityStateObservationMap ==
  [s \in ValidPayloadStates |-> ParameterizedCapabilityStateObservables(s)]

ExactStateObservationMap ==
  [s \in ValidPayloadStates |-> ExactStateObservables(s)]

PhaseOnlyRepresentationMap ==
  [s \in ValidPayloadStates |-> s.phase]

PhasePendingBindingRepresentationMap ==
  [s \in ValidPayloadStates |->
     [phase |-> s.phase,
      pending_binding |-> PendingBindingKey(s)]]

FullCanonicalRepresentationMap ==
  [s \in ValidPayloadStates |-> s]

DropBindingRepresentationMap ==
  [s \in ValidPayloadStates |->
     [phase |-> s.phase,
      previous |-> s.previous,
      authority |-> s.authority]]

DropPreviousRepresentationMap ==
  [s \in ValidPayloadStates |->
     [phase |-> s.phase,
      binding |-> s.binding,
      authority |-> s.authority]]

DropAuthorityRepresentationMap ==
  [s \in ValidPayloadStates |->
     [phase |-> s.phase,
      binding |-> s.binding,
      previous |-> s.previous]]

FaithfulProjection(representationMap, observationMap) ==
  \A x \in ValidPayloadStates, y \in ValidPayloadStates :
    representationMap[x] = representationMap[y]
      => observationMap[x] = observationMap[y]

AbsentWitness ==
  [phase |-> "ABSENT",
   binding |-> NoBindingWitness,
   previous |-> NoPreviousWitness,
   authority |-> NoAuthorityWitness]

PendingB0P0 ==
  [phase |-> "PENDING",
   binding |-> "B0",
   previous |-> "P0",
   authority |-> NoAuthorityWitness]

PendingB1P0 ==
  [phase |-> "PENDING",
   binding |-> "B1",
   previous |-> "P0",
   authority |-> NoAuthorityWitness]

PendingB0P1 ==
  [phase |-> "PENDING",
   binding |-> "B0",
   previous |-> "P1",
   authority |-> NoAuthorityWitness]

AllowB0P0A0 ==
  [phase |-> "ALLOW",
   binding |-> "B0",
   previous |-> "P0",
   authority |-> "A0"]

AllowB0P0A1 ==
  [phase |-> "ALLOW",
   binding |-> "B0",
   previous |-> "P0",
   authority |-> "A1"]

=============================================================================
