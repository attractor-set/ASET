------------------------------ MODULE SeedResolution ------------------------------
EXTENDS FiniteSets

CONSTANTS ResolutionIds, Bindings, Authorities, TerminalCommitments,
          RecognizedTerminalCommitments, NoCommitment, NoRecord

ASSUME ResolutionIds # {}
ASSUME Bindings # {}
ASSUME Authorities # {}
ASSUME RecognizedTerminalCommitments \subseteq TerminalCommitments
ASSUME NoCommitment \notin TerminalCommitments
ASSUME NoRecord \notin {"ALLOW", "BLOCK"}

Resolutions == {"UNKNOWN", "ALLOW", "BLOCK"}
TerminalResolutions == {"ALLOW", "BLOCK"}

(*
The formal model is a bounded safety projection of the minimal Seed kernel.
Authority-proof construction is abstracted as the static relation
`authorityProofBindings`; recognized prior terminal-record commitments are
abstracted as `RecognizedTerminalCommitments`. The executable oracle and
conformance corpus validate the corresponding concrete evidence boundaries.
*)
VARIABLES
    localAuthorityBindings,
    authorityProofBindings,
    requests,
    requestBinding,
    requestAuthority,
    previousResolutionCommitment,
    terminalRecord,
    terminalBinding,
    terminalAuthority,
    conflicts,
    invalidMaterial,
    observedInputs

canonicalVars ==
    <<localAuthorityBindings,
      authorityProofBindings,
      requests,
      requestBinding,
      requestAuthority,
      previousResolutionCommitment,
      terminalRecord,
      terminalBinding,
      terminalAuthority,
      conflicts,
      invalidMaterial,
      observedInputs>>

vars ==
    <<localAuthorityBindings,
      authorityProofBindings,
      requests,
      requestBinding,
      requestAuthority,
      previousResolutionCommitment,
      terminalRecord,
      terminalBinding,
      terminalAuthority,
      conflicts,
      invalidMaterial,
      observedInputs>>

Init ==
  /\ localAuthorityBindings \in SUBSET (Authorities \X Bindings)
  /\ authorityProofBindings \in SUBSET (Authorities \X Bindings)
  /\ localAuthorityBindings \subseteq authorityProofBindings
  /\ requests = {}
  /\ requestBinding = [r \in ResolutionIds |-> CHOOSE b \in Bindings : TRUE]
  /\ requestAuthority = [r \in ResolutionIds |-> CHOOSE a \in Authorities : TRUE]
  /\ previousResolutionCommitment = [r \in ResolutionIds |-> NoCommitment]
  /\ terminalRecord = [r \in ResolutionIds |-> NoRecord]
  /\ terminalBinding = [r \in ResolutionIds |-> CHOOSE b \in Bindings : TRUE]
  /\ terminalAuthority = [r \in ResolutionIds |-> CHOOSE a \in Authorities : TRUE]
  /\ conflicts = {}
  /\ invalidMaterial = {}
  /\ observedInputs = {}

RegisterRequest(r, b, a, previous) ==
  /\ r \in ResolutionIds \ requests
  /\ b \in Bindings
  /\ a \in Authorities
  /\ <<a, b>> \in localAuthorityBindings
  /\ \/ previous = NoCommitment
     \/ previous \in RecognizedTerminalCommitments
  /\ requests' = requests \cup {r}
  /\ requestBinding' = [requestBinding EXCEPT ![r] = b]
  /\ requestAuthority' = [requestAuthority EXCEPT ![r] = a]
  /\ previousResolutionCommitment' = [previousResolutionCommitment EXCEPT ![r] = previous]
  /\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  terminalRecord,
                  terminalBinding,
                  terminalAuthority,
                  conflicts,
                  invalidMaterial,
                  observedInputs>>

SubmitResolution(r, b, a, value) ==
  /\ r \in requests
  /\ b = requestBinding[r]
  /\ a \in Authorities
  /\ <<a, b>> \in authorityProofBindings
  /\ value \in TerminalResolutions
  /\ terminalRecord[r] = NoRecord
  /\ r \notin conflicts
  /\ terminalRecord' = [terminalRecord EXCEPT ![r] = value]
  /\ terminalBinding' = [terminalBinding EXCEPT ![r] = b]
  /\ terminalAuthority' = [terminalAuthority EXCEPT ![r] = a]
  /\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  requests,
                  requestBinding,
                  requestAuthority,
                  previousResolutionCommitment,
                  conflicts,
                  invalidMaterial,
                  observedInputs>>

ObserveConflict(r) ==
  /\ r \in ResolutionIds
  /\ conflicts' = conflicts \cup {r}
  /\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  requests,
                  requestBinding,
                  requestAuthority,
                  previousResolutionCommitment,
                  terminalRecord,
                  terminalBinding,
                  terminalAuthority,
                  invalidMaterial,
                  observedInputs>>

ObserveInvalidMaterial(r) ==
  /\ r \in ResolutionIds
  /\ invalidMaterial' = invalidMaterial \cup {r}
  /\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  requests,
                  requestBinding,
                  requestAuthority,
                  previousResolutionCommitment,
                  terminalRecord,
                  terminalBinding,
                  terminalAuthority,
                  conflicts,
                  observedInputs>>

ObserveNonAuthoritativeInput(r) ==
  /\ r \in ResolutionIds
  /\ observedInputs' = observedInputs \cup {r}
  /\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  requests,
                  requestBinding,
                  requestAuthority,
                  previousResolutionCommitment,
                  terminalRecord,
                  terminalBinding,
                  terminalAuthority,
                  conflicts,
                  invalidMaterial>>

Evaluate == UNCHANGED vars

RecognizedCanonicalTransition ==
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        previous \in TerminalCommitments \cup {NoCommitment} :
        RegisterRequest(r, b, a, previous)
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        value \in TerminalResolutions :
        SubmitResolution(r, b, a, value)
  \/ \E r \in ResolutionIds : ObserveConflict(r)
  \/ \E r \in ResolutionIds : ObserveInvalidMaterial(r)
  \/ \E r \in ResolutionIds : ObserveNonAuthoritativeInput(r)

Next ==
  \/ RecognizedCanonicalTransition
  \/ Evaluate

ResolutionOf(r) ==
  IF r \notin requests \/ r \in conflicts
  THEN "UNKNOWN"
  ELSE IF terminalRecord[r] = NoRecord
       THEN "UNKNOWN"
       ELSE terminalRecord[r]

EffectPermitted(r) == ResolutionOf(r) = "ALLOW"

TypeOK ==
  /\ localAuthorityBindings \subseteq Authorities \X Bindings
  /\ authorityProofBindings \subseteq Authorities \X Bindings
  /\ localAuthorityBindings \subseteq authorityProofBindings
  /\ requests \subseteq ResolutionIds
  /\ requestBinding \in [ResolutionIds -> Bindings]
  /\ requestAuthority \in [ResolutionIds -> Authorities]
  /\ previousResolutionCommitment \in [ResolutionIds -> TerminalCommitments \cup {NoCommitment}]
  /\ terminalRecord \in [ResolutionIds -> TerminalResolutions \cup {NoRecord}]
  /\ terminalBinding \in [ResolutionIds -> Bindings]
  /\ terminalAuthority \in [ResolutionIds -> Authorities]
  /\ conflicts \subseteq ResolutionIds
  /\ invalidMaterial \subseteq ResolutionIds
  /\ observedInputs \subseteq ResolutionIds

ResolutionDomain ==
  \A r \in ResolutionIds : ResolutionOf(r) \in Resolutions

AllowSoundness ==
  \A r \in ResolutionIds :
    EffectPermitted(r) =>
      /\ r \in requests
      /\ r \notin conflicts
      /\ terminalRecord[r] = "ALLOW"
      /\ terminalBinding[r] = requestBinding[r]
      /\ <<terminalAuthority[r], requestBinding[r]>> \in authorityProofBindings

FailClosed ==
  \A r \in ResolutionIds :
    ResolutionOf(r) # "ALLOW" => ~EffectPermitted(r)

ExactBinding ==
  \A r \in requests :
    terminalRecord[r] = NoRecord \/ terminalBinding[r] = requestBinding[r]

LocalAuthorityRoot ==
  \A r \in requests :
    <<requestAuthority[r], requestBinding[r]>> \in localAuthorityBindings

DelegatedAuthoritySound ==
  /\ localAuthorityBindings \subseteq authorityProofBindings
  /\ \A r \in requests :
       terminalRecord[r] = NoRecord \/
         <<terminalAuthority[r], requestBinding[r]>> \in authorityProofBindings

InputsNonAuthoritative ==
  \A r \in observedInputs :
    terminalRecord[r] = NoRecord => ResolutionOf(r) = "UNKNOWN"

TerminalUnique ==
  \A r \in ResolutionIds :
    r \in conflicts => ResolutionOf(r) = "UNKNOWN"

InvalidOrConflictUnknown ==
  \A r \in ResolutionIds :
    /\ (r \in conflicts => ResolutionOf(r) = "UNKNOWN")
    /\ (r \in invalidMaterial /\ terminalRecord[r] = NoRecord =>
          ResolutionOf(r) = "UNKNOWN")

FreshReconsideration ==
  \A r \in requests :
    \/ previousResolutionCommitment[r] = NoCommitment
    \/ previousResolutionCommitment[r] \in RecognizedTerminalCommitments

RequestsAppendOnlyStep ==
  requests \subseteq requests'

RequestsAppendOnly ==
  [][RequestsAppendOnlyStep]_vars

TerminalRecordsImmutableStep ==
  \A r \in ResolutionIds :
    terminalRecord[r] # NoRecord =>
      /\ terminalRecord'[r] = terminalRecord[r]
      /\ terminalBinding'[r] = terminalBinding[r]
      /\ terminalAuthority'[r] = terminalAuthority[r]

TerminalRecordsImmutable ==
  [][TerminalRecordsImmutableStep]_vars

CanonicalStateChangesOnlyByRecognizedTransitionStep ==
  canonicalVars' # canonicalVars => RecognizedCanonicalTransition

CanonicalStateChangesOnlyByRecognizedTransition ==
  [][CanonicalStateChangesOnlyByRecognizedTransitionStep]_vars

ObservedInputsAppendOnlyStep ==
  observedInputs \subseteq observedInputs'

ObservedInputsAppendOnly ==
  [][ObservedInputsAppendOnlyStep]_vars

Spec == Init /\ [][Next]_vars
=================================================================================
