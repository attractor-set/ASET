------------------------------ MODULE SeedResolution ------------------------------
EXTENDS FiniteSets, Naturals

CONSTANTS ResolutionIds, Bindings, Authorities, NoResolution, NoRecord

ASSUME ResolutionIds # {}
ASSUME Bindings # {}
ASSUME Authorities # {}
ASSUME NoResolution \notin ResolutionIds
ASSUME NoRecord \notin {"ALLOW", "BLOCK"}

Resolutions == {"UNKNOWN", "ALLOW", "BLOCK"}
TerminalResolutions == {"ALLOW", "BLOCK"}

(*
The formal model is a bounded safety projection of the minimal Seed kernel.
Authority-proof construction is abstracted as the static relation
`authorityProofBindings`; the executable oracle and conformance corpus validate
exact grant-chain, acyclicity and non-expansion details.
*)
VARIABLES
    localAuthorityBindings,
    authorityProofBindings,
    requests,
    requestBinding,
    requestAuthority,
    previousResolution,
    terminalRecord,
    terminalBinding,
    terminalAuthority,
    conflicts,
    invalidMaterial,
    observedInputs,
    rejectedCount

canonicalVars ==
    <<localAuthorityBindings,
      authorityProofBindings,
      requests,
      requestBinding,
      requestAuthority,
      previousResolution,
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
      previousResolution,
      terminalRecord,
      terminalBinding,
      terminalAuthority,
      conflicts,
      invalidMaterial,
      observedInputs,
      rejectedCount>>

Init ==
  /\ localAuthorityBindings \in SUBSET (Authorities \X Bindings)
  /\ authorityProofBindings \in SUBSET (Authorities \X Bindings)
  /\ localAuthorityBindings \subseteq authorityProofBindings
  /\ requests = {}
  /\ requestBinding = [r \in ResolutionIds |-> CHOOSE b \in Bindings : TRUE]
  /\ requestAuthority = [r \in ResolutionIds |-> CHOOSE a \in Authorities : TRUE]
  /\ previousResolution = [r \in ResolutionIds |-> NoResolution]
  /\ terminalRecord = [r \in ResolutionIds |-> NoRecord]
  /\ terminalBinding = [r \in ResolutionIds |-> CHOOSE b \in Bindings : TRUE]
  /\ terminalAuthority = [r \in ResolutionIds |-> CHOOSE a \in Authorities : TRUE]
  /\ conflicts = {}
  /\ invalidMaterial = {}
  /\ observedInputs = {}
  /\ rejectedCount = 0

RegisterRequest(r, b, a, previous) ==
  /\ r \in ResolutionIds \ requests
  /\ b \in Bindings
  /\ a \in Authorities
  /\ <<a, b>> \in localAuthorityBindings
  /\ \/ previous = NoResolution
     \/ /\ previous \in requests
        /\ previous # r
        /\ terminalRecord[previous] \in TerminalResolutions
        /\ previous \notin conflicts
  /\ requests' = requests \cup {r}
  /\ requestBinding' = [requestBinding EXCEPT ![r] = b]
  /\ requestAuthority' = [requestAuthority EXCEPT ![r] = a]
  /\ previousResolution' = [previousResolution EXCEPT ![r] = previous]
  /\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  terminalRecord,
                  terminalBinding,
                  terminalAuthority,
                  conflicts,
                  invalidMaterial,
                  observedInputs,
                  rejectedCount>>

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
                  previousResolution,
                  conflicts,
                  invalidMaterial,
                  observedInputs,
                  rejectedCount>>

ObserveConflict(r) ==
  /\ r \in ResolutionIds
  /\ conflicts' = conflicts \cup {r}
  /\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  requests,
                  requestBinding,
                  requestAuthority,
                  previousResolution,
                  terminalRecord,
                  terminalBinding,
                  terminalAuthority,
                  invalidMaterial,
                  observedInputs,
                  rejectedCount>>

ObserveInvalidMaterial(r) ==
  /\ r \in ResolutionIds
  /\ invalidMaterial' = invalidMaterial \cup {r}
  /\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  requests,
                  requestBinding,
                  requestAuthority,
                  previousResolution,
                  terminalRecord,
                  terminalBinding,
                  terminalAuthority,
                  conflicts,
                  observedInputs,
                  rejectedCount>>

ObserveNonAuthoritativeInput(r) ==
  /\ r \in ResolutionIds
  /\ observedInputs' = observedInputs \cup {r}
  /\ UNCHANGED <<localAuthorityBindings,
                  authorityProofBindings,
                  requests,
                  requestBinding,
                  requestAuthority,
                  previousResolution,
                  terminalRecord,
                  terminalBinding,
                  terminalAuthority,
                  conflicts,
                  invalidMaterial,
                  rejectedCount>>

RejectOperation ==
  /\ rejectedCount' = rejectedCount + 1
  /\ UNCHANGED canonicalVars

Evaluate == UNCHANGED vars

Next ==
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        previous \in ResolutionIds \cup {NoResolution} :
        RegisterRequest(r, b, a, previous)
  \/ \E r \in ResolutionIds, b \in Bindings, a \in Authorities,
        value \in TerminalResolutions :
        SubmitResolution(r, b, a, value)
  \/ \E r \in ResolutionIds : ObserveConflict(r)
  \/ \E r \in ResolutionIds : ObserveInvalidMaterial(r)
  \/ \E r \in ResolutionIds : ObserveNonAuthoritativeInput(r)
  \/ RejectOperation
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
  /\ previousResolution \in [ResolutionIds -> ResolutionIds \cup {NoResolution}]
  /\ terminalRecord \in [ResolutionIds -> TerminalResolutions \cup {NoRecord}]
  /\ terminalBinding \in [ResolutionIds -> Bindings]
  /\ terminalAuthority \in [ResolutionIds -> Authorities]
  /\ conflicts \subseteq ResolutionIds
  /\ invalidMaterial \subseteq ResolutionIds
  /\ observedInputs \subseteq ResolutionIds
  /\ rejectedCount \in Nat

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
    \/ previousResolution[r] = NoResolution
    \/ /\ previousResolution[r] \in requests
       /\ previousResolution[r] # r
       /\ terminalRecord[previousResolution[r]] \in TerminalResolutions

RequestsAppendOnly == [] (requests \subseteq requests')

TerminalRecordsImmutable ==
  [] (\A r \in ResolutionIds :
        terminalRecord[r] # NoRecord =>
          /\ terminalRecord'[r] = terminalRecord[r]
          /\ terminalBinding'[r] = terminalBinding[r]
          /\ terminalAuthority'[r] = terminalAuthority[r])

RejectedOperationPreservesStore ==
  [] (rejectedCount' > rejectedCount => UNCHANGED canonicalVars)

ObservedInputsAppendOnly == [] (observedInputs \subseteq observedInputs')

Spec == Init /\ [][Next]_vars
=================================================================================
