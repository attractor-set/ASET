------------------------- MODULE SeedResolutionProofs -------------------------

EXTENDS SeedResolution, TLAPS

(*
The first unbounded proof layer covers the pure resolution evaluator.

It does not yet claim:
- inductiveness of the complete state invariant;
- preservation by every Next action;
- temporal safety of Spec;
- liveness;
- cryptographic correctness;
- implementation conformance.
*)

ASSUME NoRecordIsNotTerminal == NoRecord \notin {"ALLOW", "BLOCK"}

THEOREM EffectPermissionDefinition ==
  \A r \in ResolutionIds :
    EffectPermitted(r) <=> ResolutionOf(r) = "ALLOW"
PROOF
  BY DEF EffectPermitted


THEOREM UnregisteredResolutionIsUnknown ==
  \A r \in ResolutionIds :
    r \notin requests => ResolutionOf(r) = "UNKNOWN"
PROOF
  BY DEF ResolutionOf


THEOREM ConflictedResolutionIsUnknown ==
  \A r \in ResolutionIds :
    r \in conflicts => ResolutionOf(r) = "UNKNOWN"
PROOF
  BY DEF ResolutionOf


THEOREM MissingTerminalRecordIsUnknown ==
  \A r \in ResolutionIds :
    terminalRecord[r] = NoRecord => ResolutionOf(r) = "UNKNOWN"
PROOF
  BY DEF ResolutionOf


THEOREM AllowResolutionCharacterization ==
  \A r \in ResolutionIds :
    EffectPermitted(r) <=>
      /\ r \in requests
      /\ r \notin conflicts
      /\ terminalRecord[r] = "ALLOW"
PROOF
  BY NoRecordIsNotTerminal DEF EffectPermitted, ResolutionOf


THEOREM BlockResolutionCharacterization ==
  \A r \in ResolutionIds :
    ResolutionOf(r) = "BLOCK" <=>
      /\ r \in requests
      /\ r \notin conflicts
      /\ terminalRecord[r] = "BLOCK"
PROOF
  BY NoRecordIsNotTerminal DEF ResolutionOf


THEOREM NoAllowWithoutTerminalAllow ==
  \A r \in ResolutionIds :
    terminalRecord[r] # "ALLOW" => ~EffectPermitted(r)
PROOF
  BY DEF EffectPermitted, ResolutionOf

THEOREM ResolutionDomainPointwise ==
  ASSUME TypeOK,
         NEW r \in ResolutionIds
  PROVE ResolutionOf(r) \in Resolutions
PROOF
  <1>1. terminalRecord[r] \in TerminalResolutions \cup {NoRecord}
    BY DEF TypeOK

  <1>2. CASE r \notin requests \/ r \in conflicts
    <2>1. QED
      BY <1>2
         DEF ResolutionOf, Resolutions

  <1>3. CASE
          /\ ~(r \notin requests \/ r \in conflicts)
          /\ terminalRecord[r] = NoRecord
    <2>1. QED
      BY <1>3
         DEF ResolutionOf, Resolutions

  <1>4. CASE
          /\ ~(r \notin requests \/ r \in conflicts)
          /\ terminalRecord[r] # NoRecord
    <2>1. QED
      BY <1>1, <1>4
         DEF ResolutionOf, Resolutions, TerminalResolutions

  <1>5. QED
    BY <1>2, <1>3, <1>4


THEOREM ResolutionDomainFromTypeOK ==
  TypeOK => ResolutionDomain
PROOF
  BY ResolutionDomainPointwise
     DEF ResolutionDomain


THEOREM FailClosedByEvaluator ==
  FailClosed
PROOF
  BY DEF FailClosed, EffectPermitted


THEOREM InputsNonAuthoritativeFromTypeOK ==
  TypeOK => InputsNonAuthoritative
PROOF
  BY MissingTerminalRecordIsUnknown
     DEF TypeOK, InputsNonAuthoritative


THEOREM TerminalUniqueByEvaluator ==
  TerminalUnique
PROOF
  BY ConflictedResolutionIsUnknown
     DEF TerminalUnique


THEOREM InvalidOrConflictUnknownByEvaluator ==
  InvalidOrConflictUnknown
PROOF
  BY ConflictedResolutionIsUnknown,
     MissingTerminalRecordIsUnknown
     DEF InvalidOrConflictUnknown


THEOREM AllowSoundnessPointwise ==
  ASSUME ExactBinding,
         DelegatedAuthoritySound,
         NEW r \in ResolutionIds,
         EffectPermitted(r)
  PROVE
    /\ r \in requests
    /\ r \notin conflicts
    /\ terminalRecord[r] = "ALLOW"
    /\ terminalBinding[r] = requestBinding[r]
    /\ <<terminalAuthority[r], requestBinding[r]>>
         \in authorityProofBindings
PROOF
  <1>1.
    /\ r \in requests
    /\ r \notin conflicts
    /\ terminalRecord[r] = "ALLOW"
    BY AllowResolutionCharacterization

  <1>2. terminalRecord[r] # NoRecord
    BY <1>1, NoRecordIsNotTerminal

  <1>3. terminalBinding[r] = requestBinding[r]
    BY <1>1, <1>2
       DEF ExactBinding

  <1>4.
    <<terminalAuthority[r], requestBinding[r]>>
      \in authorityProofBindings
    BY <1>1, <1>2
       DEF DelegatedAuthoritySound

  <1>5. QED
    BY <1>1, <1>3, <1>4


THEOREM AllowSoundnessFromStructuralInvariants ==
  ExactBinding /\ DelegatedAuthoritySound
    => AllowSoundness
PROOF
  BY AllowSoundnessPointwise
     DEF AllowSoundness


SeedStateSafety ==
  /\ TypeOK
  /\ ResolutionDomain
  /\ AllowSoundness
  /\ FailClosed
  /\ ExactBinding
  /\ LocalAuthorityRoot
  /\ DelegatedAuthoritySound
  /\ InputsNonAuthoritative
  /\ TerminalUnique
  /\ InvalidOrConflictUnknown
  /\ FreshReconsideration


TerminalRecordRequiresRequest ==
  \A r \in ResolutionIds :
    terminalRecord[r] # NoRecord => r \in requests


InductiveInvariant ==
  /\ TypeOK
  /\ TerminalRecordRequiresRequest
  /\ ExactBinding
  /\ LocalAuthorityRoot
  /\ DelegatedAuthoritySound
  /\ FreshReconsideration


THEOREM InductiveInvariantImpliesSeedStateSafety ==
  InductiveInvariant => SeedStateSafety
PROOF
  BY ResolutionDomainFromTypeOK,
     AllowSoundnessFromStructuralInvariants,
     FailClosedByEvaluator,
     InputsNonAuthoritativeFromTypeOK,
     TerminalUniqueByEvaluator,
     InvalidOrConflictUnknownByEvaluator
     DEF InductiveInvariant, SeedStateSafety


ASSUME BindingsNonempty ==
  Bindings # {}

ASSUME AuthoritiesNonempty ==
  Authorities # {}


THEOREM ChosenBindingInBindings ==
  (CHOOSE b \in Bindings : TRUE) \in Bindings
PROOF
  BY BindingsNonempty


THEOREM ChosenAuthorityInAuthorities ==
  (CHOOSE a \in Authorities : TRUE) \in Authorities
PROOF
  BY AuthoritiesNonempty


THEOREM InitImpliesTypeOK ==
  Init => TypeOK
PROOF
  BY ChosenBindingInBindings,
     ChosenAuthorityInAuthorities
     DEF Init, TypeOK, TerminalResolutions


THEOREM InitImpliesExactBinding ==
  Init => ExactBinding
PROOF
  BY DEF Init, ExactBinding


THEOREM InitImpliesLocalAuthorityRoot ==
  Init => LocalAuthorityRoot
PROOF
  BY DEF Init, LocalAuthorityRoot


THEOREM InitImpliesDelegatedAuthoritySound ==
  Init => DelegatedAuthoritySound
PROOF
  BY DEF Init, DelegatedAuthoritySound


THEOREM InitImpliesFreshReconsideration ==
  Init => FreshReconsideration
PROOF
  BY DEF Init, FreshReconsideration


THEOREM InitImpliesTerminalRecordRequiresRequest ==
  Init => TerminalRecordRequiresRequest
PROOF
  BY DEF Init, TerminalRecordRequiresRequest


THEOREM InitImpliesInductiveInvariant ==
  Init => InductiveInvariant
PROOF
  BY InitImpliesTypeOK,
     InitImpliesTerminalRecordRequiresRequest,
     InitImpliesExactBinding,
     InitImpliesLocalAuthorityRoot,
     InitImpliesDelegatedAuthoritySound,
     InitImpliesFreshReconsideration
     DEF InductiveInvariant


THEOREM UnrequestedHasNoTerminalRecord ==
  ASSUME TerminalRecordRequiresRequest,
         NEW r \in ResolutionIds,
         r \notin requests
  PROVE terminalRecord[r] = NoRecord
PROOF
  BY DEF TerminalRecordRequiresRequest


THEOREM RegisterRequestPreservesTypeOK ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE TypeOK'
PROOF
  BY DEF RegisterRequest, InductiveInvariant, TypeOK


THEOREM RegisterRequestPreservesTerminalRecordRequiresRequest ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE TerminalRecordRequiresRequest'
PROOF
  BY DEF RegisterRequest,
         InductiveInvariant,
         TerminalRecordRequiresRequest


THEOREM RegisterRequestNewKeyValues ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE
    /\ requestBinding'[r] = b
    /\ requestAuthority'[r] = a
    /\ previousResolution'[r] = previous
PROOF
  BY DEF RegisterRequest, InductiveInvariant, TypeOK


THEOREM RegisterRequestOldKeyValues ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous),
         NEW q \in requests,
         q # r
  PROVE
    /\ requestBinding'[q] = requestBinding[q]
    /\ requestAuthority'[q] = requestAuthority[q]
    /\ previousResolution'[q] = previousResolution[q]
PROOF
  BY DEF RegisterRequest, InductiveInvariant, TypeOK


THEOREM RegisterRequestUnchangedValues ==
  ASSUME NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE
    /\ localAuthorityBindings' = localAuthorityBindings
    /\ authorityProofBindings' = authorityProofBindings
    /\ terminalRecord' = terminalRecord
    /\ terminalBinding' = terminalBinding
    /\ terminalAuthority' = terminalAuthority
PROOF
  BY DEF RegisterRequest


THEOREM RegisterRequestSetFacts ==
  ASSUME NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE
    /\ requests' = requests \cup {r}
    /\ requests \subseteq requests'
PROOF
  BY DEF RegisterRequest


THEOREM RegisterRequestPreviousGuard ==
  ASSUME NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE
    \/ previous = NoResolution
    \/ /\ previous \in requests
       /\ previous # r
       /\ terminalRecord[previous] \in TerminalResolutions
PROOF
  BY DEF RegisterRequest


THEOREM RegisterRequestPreservesExactBindingPointwise ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous),
         NEW q \in requests'
  PROVE
    terminalRecord'[q] = NoRecord \/
      terminalBinding'[q] = requestBinding'[q]
PROOF
  <1>1. CASE q = r
    <2>1. terminalRecord[r] = NoRecord
      BY DEF RegisterRequest,
             InductiveInvariant,
             TerminalRecordRequiresRequest

    <2>2. terminalRecord' = terminalRecord
      BY RegisterRequestUnchangedValues

    <2>3. QED
      BY <1>1, <2>1, <2>2

  <1>2. CASE q # r
    <2>1. q \in requests
      BY <1>2
         DEF RegisterRequest

    <2>2.
      terminalRecord[q] = NoRecord \/
        terminalBinding[q] = requestBinding[q]
      BY <2>1
         DEF InductiveInvariant, ExactBinding

    <2>3.
      /\ requestBinding'[q] = requestBinding[q]
      /\ terminalRecord'[q] = terminalRecord[q]
      /\ terminalBinding'[q] = terminalBinding[q]
      BY <1>2, <2>1,
         RegisterRequestOldKeyValues,
         RegisterRequestUnchangedValues

    <2>4. QED
      BY <2>2, <2>3

  <1>3. QED
    BY <1>1, <1>2


THEOREM RegisterRequestPreservesExactBinding ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE ExactBinding'
PROOF
  BY RegisterRequestPreservesExactBindingPointwise
     DEF ExactBinding


THEOREM RegisterRequestPreservesLocalAuthorityRootPointwise ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous),
         NEW q \in requests'
  PROVE
    <<requestAuthority'[q], requestBinding'[q]>>
      \in localAuthorityBindings'
PROOF
  <1>1. CASE q = r
    <2>1. <<a, b>> \in localAuthorityBindings
      BY DEF RegisterRequest

    <2>2.
      /\ requestAuthority'[q] = a
      /\ requestBinding'[q] = b
      /\ localAuthorityBindings' = localAuthorityBindings
      BY <1>1,
         RegisterRequestNewKeyValues,
         RegisterRequestUnchangedValues

    <2>3. QED
      BY <2>1, <2>2

  <1>2. CASE q # r
    <2>1. q \in requests
      BY <1>2
         DEF RegisterRequest

    <2>2.
      <<requestAuthority[q], requestBinding[q]>>
        \in localAuthorityBindings
      BY <2>1
         DEF InductiveInvariant, LocalAuthorityRoot

    <2>3.
      /\ requestAuthority'[q] = requestAuthority[q]
      /\ requestBinding'[q] = requestBinding[q]
      /\ localAuthorityBindings' = localAuthorityBindings
      BY <1>2, <2>1,
         RegisterRequestOldKeyValues,
         RegisterRequestUnchangedValues

    <2>4. QED
      BY <2>2, <2>3

  <1>3. QED
    BY <1>1, <1>2


THEOREM RegisterRequestPreservesLocalAuthorityRoot ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE LocalAuthorityRoot'
PROOF
  BY RegisterRequestPreservesLocalAuthorityRootPointwise
     DEF LocalAuthorityRoot


THEOREM RegisterRequestPreservesDelegatedAuthorityPointwise ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous),
         NEW q \in requests'
  PROVE
    terminalRecord'[q] = NoRecord \/
      <<terminalAuthority'[q], requestBinding'[q]>>
        \in authorityProofBindings'
PROOF
  <1>1. CASE q = r
    <2>1. terminalRecord[r] = NoRecord
      BY DEF RegisterRequest,
             InductiveInvariant,
             TerminalRecordRequiresRequest

    <2>2. terminalRecord' = terminalRecord
      BY RegisterRequestUnchangedValues

    <2>3. QED
      BY <1>1, <2>1, <2>2

  <1>2. CASE q # r
    <2>1. q \in requests
      BY <1>2
         DEF RegisterRequest

    <2>2.
      terminalRecord[q] = NoRecord \/
        <<terminalAuthority[q], requestBinding[q]>>
          \in authorityProofBindings
      BY <2>1
         DEF InductiveInvariant, DelegatedAuthoritySound

    <2>3.
      /\ terminalRecord'[q] = terminalRecord[q]
      /\ terminalAuthority'[q] = terminalAuthority[q]
      /\ requestBinding'[q] = requestBinding[q]
      /\ authorityProofBindings' = authorityProofBindings
      BY <1>2, <2>1,
         RegisterRequestOldKeyValues,
         RegisterRequestUnchangedValues

    <2>4. QED
      BY <2>2, <2>3

  <1>3. QED
    BY <1>1, <1>2


THEOREM RegisterRequestPreservesDelegatedAuthoritySound ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE DelegatedAuthoritySound'
PROOF
  <1>1.
    localAuthorityBindings' \subseteq authorityProofBindings'
    BY RegisterRequestUnchangedValues
       DEF InductiveInvariant, DelegatedAuthoritySound

  <1>2.
    \A q \in requests' :
      terminalRecord'[q] = NoRecord \/
        <<terminalAuthority'[q], requestBinding'[q]>>
          \in authorityProofBindings'
    BY RegisterRequestPreservesDelegatedAuthorityPointwise

  <1>3. QED
    BY <1>1, <1>2
       DEF DelegatedAuthoritySound


THEOREM RegisterRequestPreservesFreshReconsiderationPointwise ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous),
         NEW q \in requests'
  PROVE
    \/ previousResolution'[q] = NoResolution
    \/ /\ previousResolution'[q] \in requests'
       /\ previousResolution'[q] # q
       /\ terminalRecord'[previousResolution'[q]]
            \in TerminalResolutions
PROOF
  <1>1. CASE q = r
    <2>1.
      /\ previousResolution'[q] = previous
      /\ requests' = requests \cup {r}
      /\ terminalRecord' = terminalRecord
      BY <1>1,
         RegisterRequestNewKeyValues,
         RegisterRequestSetFacts,
         RegisterRequestUnchangedValues

    <2>2.
      \/ previous = NoResolution
      \/ /\ previous \in requests
         /\ previous # r
         /\ terminalRecord[previous] \in TerminalResolutions
      BY RegisterRequestPreviousGuard

    <2>3. QED
      BY <1>1, <2>1, <2>2

  <1>2. CASE q # r
    <2>1. q \in requests
      BY <1>2
         DEF RegisterRequest

    <2>2.
      \/ previousResolution[q] = NoResolution
      \/ /\ previousResolution[q] \in requests
         /\ previousResolution[q] # q
         /\ terminalRecord[previousResolution[q]]
              \in TerminalResolutions
      BY <2>1
         DEF InductiveInvariant, FreshReconsideration

    <2>3.
      /\ previousResolution'[q] = previousResolution[q]
      /\ requests \subseteq requests'
      /\ terminalRecord' = terminalRecord
      BY <1>2, <2>1,
         RegisterRequestOldKeyValues,
         RegisterRequestSetFacts,
         RegisterRequestUnchangedValues

    <2>4. QED
      BY <2>2, <2>3

  <1>3. QED
    BY <1>1, <1>2


THEOREM RegisterRequestPreservesFreshReconsideration ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE FreshReconsideration'
PROOF
  BY RegisterRequestPreservesFreshReconsiderationPointwise
     DEF FreshReconsideration



THEOREM RegisterRequestPreservesInductiveInvariant ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE InductiveInvariant'
PROOF
  BY RegisterRequestPreservesTypeOK,
     RegisterRequestPreservesTerminalRecordRequiresRequest,
     RegisterRequestPreservesExactBinding,
     RegisterRequestPreservesLocalAuthorityRoot,
     RegisterRequestPreservesDelegatedAuthoritySound,
     RegisterRequestPreservesFreshReconsideration
     DEF InductiveInvariant


THEOREM SubmitResolutionNewKeyValues ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value)
  PROVE
    /\ terminalRecord'[r] = value
    /\ terminalBinding'[r] = b
    /\ terminalAuthority'[r] = a
PROOF
  BY DEF SubmitResolution, InductiveInvariant, TypeOK


THEOREM SubmitResolutionOldKeyValues ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value),
         NEW q \in ResolutionIds,
         q # r
  PROVE
    /\ terminalRecord'[q] = terminalRecord[q]
    /\ terminalBinding'[q] = terminalBinding[q]
    /\ terminalAuthority'[q] = terminalAuthority[q]
PROOF
  BY DEF SubmitResolution, InductiveInvariant, TypeOK


THEOREM SubmitResolutionUnchangedValues ==
  ASSUME NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value)
  PROVE
    /\ localAuthorityBindings' = localAuthorityBindings
    /\ authorityProofBindings' = authorityProofBindings
    /\ requests' = requests
    /\ requestBinding' = requestBinding
    /\ requestAuthority' = requestAuthority
    /\ previousResolution' = previousResolution
PROOF
  BY DEF SubmitResolution


THEOREM SubmitResolutionGuardFacts ==
  ASSUME NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value)
  PROVE
    /\ r \in requests
    /\ b = requestBinding[r]
    /\ <<a, b>> \in authorityProofBindings
    /\ value \in TerminalResolutions
    /\ terminalRecord[r] = NoRecord
    /\ r \notin conflicts
PROOF
  BY DEF SubmitResolution


THEOREM SubmitResolutionPreservesTypeOK ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value)
  PROVE TypeOK'
PROOF
  BY DEF SubmitResolution,
         InductiveInvariant,
         TypeOK,
         TerminalResolutions


THEOREM SubmitResolutionPreservesTerminalRecordRequiresRequestPointwise ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value),
         NEW q \in ResolutionIds,
         terminalRecord'[q] # NoRecord
  PROVE q \in requests'
PROOF
  <1>1. CASE q = r
    <2>1. r \in requests
      BY SubmitResolutionGuardFacts

    <2>2. requests' = requests
      BY SubmitResolutionUnchangedValues

    <2>3. QED
      BY <1>1, <2>1, <2>2

  <1>2. CASE q # r
    <2>1. terminalRecord'[q] = terminalRecord[q]
      BY <1>2,
         SubmitResolutionOldKeyValues

    <2>2. terminalRecord[q] # NoRecord
      BY <2>1

    <2>3. q \in requests
      BY <2>2
         DEF InductiveInvariant,
             TerminalRecordRequiresRequest

    <2>4. requests' = requests
      BY SubmitResolutionUnchangedValues

    <2>5. QED
      BY <2>3, <2>4

  <1>3. QED
    BY <1>1, <1>2


THEOREM SubmitResolutionPreservesTerminalRecordRequiresRequest ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value)
  PROVE TerminalRecordRequiresRequest'
PROOF
  BY SubmitResolutionPreservesTerminalRecordRequiresRequestPointwise
     DEF TerminalRecordRequiresRequest


THEOREM SubmitResolutionPreservesExactBindingPointwise ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value),
         NEW q \in requests'
  PROVE
    terminalRecord'[q] = NoRecord \/
      terminalBinding'[q] = requestBinding'[q]
PROOF
  <1>1. CASE q = r
    <2>1.
      /\ terminalBinding'[r] = b
      /\ b = requestBinding[r]
      /\ requestBinding' = requestBinding
      BY SubmitResolutionNewKeyValues,
         SubmitResolutionGuardFacts,
         SubmitResolutionUnchangedValues

    <2>2. QED
      BY <1>1, <2>1

  <1>2. CASE q # r
    <2>1. q \in requests
      BY <1>2,
         SubmitResolutionUnchangedValues

    <2>2.
      terminalRecord[q] = NoRecord \/
        terminalBinding[q] = requestBinding[q]
      BY <2>1
         DEF InductiveInvariant, ExactBinding

    <2>3. q \in ResolutionIds
      BY <2>1
         DEF InductiveInvariant, TypeOK

    <2>4. terminalRecord'[q] = terminalRecord[q]
      BY <1>2, <2>3,
         SubmitResolutionOldKeyValues

    <2>5. terminalBinding'[q] = terminalBinding[q]
      BY <1>2, <2>3,
         SubmitResolutionOldKeyValues

    <2>6. requestBinding' = requestBinding
      BY SubmitResolutionUnchangedValues

    <2>7. QED
      BY <2>2, <2>4, <2>5, <2>6

  <1>3. QED
    BY <1>1, <1>2


THEOREM SubmitResolutionPreservesExactBinding ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value)
  PROVE ExactBinding'
PROOF
  BY SubmitResolutionPreservesExactBindingPointwise
     DEF ExactBinding


THEOREM SubmitResolutionPreservesLocalAuthorityRoot ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value)
  PROVE LocalAuthorityRoot'
PROOF
  BY SubmitResolutionUnchangedValues
     DEF InductiveInvariant, LocalAuthorityRoot


THEOREM SubmitResolutionPreservesDelegatedAuthorityPointwise ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value),
         NEW q \in requests'
  PROVE
    terminalRecord'[q] = NoRecord \/
      <<terminalAuthority'[q], requestBinding'[q]>>
        \in authorityProofBindings'
PROOF
  <1>1. CASE q = r
    <2>1.
      /\ terminalAuthority'[r] = a
      /\ requestBinding' = requestBinding
      /\ authorityProofBindings' = authorityProofBindings
      /\ b = requestBinding[r]
      /\ <<a, b>> \in authorityProofBindings
      BY SubmitResolutionNewKeyValues,
         SubmitResolutionUnchangedValues,
         SubmitResolutionGuardFacts

    <2>2. QED
      BY <1>1, <2>1

  <1>2. CASE q # r
    <2>1. q \in requests
      BY <1>2,
         SubmitResolutionUnchangedValues

    <2>2.
      terminalRecord[q] = NoRecord \/
        <<terminalAuthority[q], requestBinding[q]>>
          \in authorityProofBindings
      BY <2>1
         DEF InductiveInvariant, DelegatedAuthoritySound

    <2>3. q \in ResolutionIds
      BY <2>1
         DEF InductiveInvariant, TypeOK

    <2>4. terminalRecord'[q] = terminalRecord[q]
      BY <1>2, <2>3,
         SubmitResolutionOldKeyValues

    <2>5. terminalAuthority'[q] = terminalAuthority[q]
      BY <1>2, <2>3,
         SubmitResolutionOldKeyValues

    <2>6. requestBinding' = requestBinding
      BY SubmitResolutionUnchangedValues

    <2>7. authorityProofBindings' = authorityProofBindings
      BY SubmitResolutionUnchangedValues

    <2>8. QED
      BY <2>2, <2>4, <2>5, <2>6, <2>7

  <1>3. QED
    BY <1>1, <1>2


THEOREM SubmitResolutionPreservesDelegatedAuthoritySound ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value)
  PROVE DelegatedAuthoritySound'
PROOF
  <1>1.
    localAuthorityBindings' \subseteq authorityProofBindings'
    BY SubmitResolutionUnchangedValues
       DEF InductiveInvariant, DelegatedAuthoritySound

  <1>2.
    \A q \in requests' :
      terminalRecord'[q] = NoRecord \/
        <<terminalAuthority'[q], requestBinding'[q]>>
          \in authorityProofBindings'
    BY SubmitResolutionPreservesDelegatedAuthorityPointwise

  <1>3. QED
    BY <1>1, <1>2
       DEF DelegatedAuthoritySound


THEOREM SubmitResolutionPreservesExistingTerminal ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value),
         NEW p \in ResolutionIds,
         terminalRecord[p] \in TerminalResolutions
  PROVE terminalRecord'[p] \in TerminalResolutions
PROOF
  <1>1. terminalRecord[r] = NoRecord
    BY SubmitResolutionGuardFacts

  <1>2. p # r
    BY <1>1, NoRecordIsNotTerminal
       DEF TerminalResolutions

  <1>3. terminalRecord'[p] = terminalRecord[p]
    BY <1>2,
       SubmitResolutionOldKeyValues

  <1>4. QED
    BY <1>3


THEOREM SubmitResolutionPreservesFreshReconsiderationPointwise ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value),
         NEW q \in requests'
  PROVE
    \/ previousResolution'[q] = NoResolution
    \/ /\ previousResolution'[q] \in requests'
       /\ previousResolution'[q] # q
       /\ terminalRecord'[previousResolution'[q]]
            \in TerminalResolutions
PROOF
  <1>1. q \in requests
    BY SubmitResolutionUnchangedValues

  <1>2.
    \/ previousResolution[q] = NoResolution
    \/ /\ previousResolution[q] \in requests
       /\ previousResolution[q] # q
       /\ terminalRecord[previousResolution[q]]
            \in TerminalResolutions
    BY <1>1
       DEF InductiveInvariant, FreshReconsideration

  <1>3.
    /\ requests' = requests
    /\ previousResolution' = previousResolution
    BY SubmitResolutionUnchangedValues

  <1>4. CASE previousResolution[q] = NoResolution
    <2>1. QED
      BY <1>3, <1>4

  <1>5. CASE previousResolution[q] # NoResolution
    <2>1.
      /\ previousResolution[q] \in requests
      /\ previousResolution[q] # q
      /\ terminalRecord[previousResolution[q]]
           \in TerminalResolutions
      BY <1>2, <1>5

    <2>2. previousResolution[q] \in ResolutionIds
      BY <2>1
         DEF InductiveInvariant, TypeOK

    <2>3. previousResolution[q] # r
      BY <2>1,
         SubmitResolutionGuardFacts,
         NoRecordIsNotTerminal
         DEF TerminalResolutions

    <2>4.
      terminalRecord'[previousResolution[q]]
        = terminalRecord[previousResolution[q]]
      BY <2>2, <2>3,
         SubmitResolutionOldKeyValues

    <2>5.
      terminalRecord'[previousResolution[q]]
        \in TerminalResolutions
      BY <2>1, <2>4

    <2>6. QED
      BY <1>3, <2>1, <2>5

  <1>6. QED
    BY <1>4, <1>5


THEOREM SubmitResolutionPreservesFreshReconsideration ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value)
  PROVE FreshReconsideration'
PROOF
  BY SubmitResolutionPreservesFreshReconsiderationPointwise
     DEF FreshReconsideration


THEOREM SubmitResolutionPreservesInductiveInvariant ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value)
  PROVE InductiveInvariant'
PROOF
  BY SubmitResolutionPreservesTypeOK,
     SubmitResolutionPreservesTerminalRecordRequiresRequest,
     SubmitResolutionPreservesExactBinding,
     SubmitResolutionPreservesLocalAuthorityRoot,
     SubmitResolutionPreservesDelegatedAuthoritySound,
     SubmitResolutionPreservesFreshReconsideration
     DEF InductiveInvariant


THEOREM ObserveConflictPreservesInductiveInvariant ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         ObserveConflict(r)
  PROVE InductiveInvariant'
PROOF
  BY DEF ObserveConflict,
         InductiveInvariant,
         TypeOK,
         TerminalRecordRequiresRequest,
         ExactBinding,
         LocalAuthorityRoot,
         DelegatedAuthoritySound,
         FreshReconsideration


THEOREM ObserveInvalidMaterialPreservesInductiveInvariant ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         ObserveInvalidMaterial(r)
  PROVE InductiveInvariant'
PROOF
  BY DEF ObserveInvalidMaterial,
         InductiveInvariant,
         TypeOK,
         TerminalRecordRequiresRequest,
         ExactBinding,
         LocalAuthorityRoot,
         DelegatedAuthoritySound,
         FreshReconsideration


THEOREM ObserveNonAuthoritativeInputPreservesInductiveInvariant ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         ObserveNonAuthoritativeInput(r)
  PROVE InductiveInvariant'
PROOF
  BY DEF ObserveNonAuthoritativeInput,
         InductiveInvariant,
         TypeOK,
         TerminalRecordRequiresRequest,
         ExactBinding,
         LocalAuthorityRoot,
         DelegatedAuthoritySound,
         FreshReconsideration


THEOREM StateStutterPreservesInductiveInvariant ==
  InductiveInvariant /\ UNCHANGED vars
    => InductiveInvariant'
PROOF
  BY DEF vars,
         InductiveInvariant,
         TypeOK,
         TerminalRecordRequiresRequest,
         ExactBinding,
         LocalAuthorityRoot,
         DelegatedAuthoritySound,
         FreshReconsideration


THEOREM EvaluatePreservesInductiveInvariant ==
  InductiveInvariant /\ Evaluate
    => InductiveInvariant'
PROOF
  BY StateStutterPreservesInductiveInvariant
     DEF Evaluate


THEOREM RecognizedCanonicalTransitionPreservesInductiveInvariant ==
  InductiveInvariant /\ RecognizedCanonicalTransition
    => InductiveInvariant'
PROOF
  BY RegisterRequestPreservesInductiveInvariant,
     SubmitResolutionPreservesInductiveInvariant,
     ObserveConflictPreservesInductiveInvariant,
     ObserveInvalidMaterialPreservesInductiveInvariant,
     ObserveNonAuthoritativeInputPreservesInductiveInvariant
     DEF RecognizedCanonicalTransition


THEOREM NextPreservesInductiveInvariant ==
  InductiveInvariant /\ Next
    => InductiveInvariant'
PROOF
  BY RecognizedCanonicalTransitionPreservesInductiveInvariant,
     EvaluatePreservesInductiveInvariant
     DEF Next


THEOREM BoxNextPreservesInductiveInvariant ==
  InductiveInvariant /\ [Next]_vars
    => InductiveInvariant'
PROOF
  BY NextPreservesInductiveInvariant,
     StateStutterPreservesInductiveInvariant


THEOREM SpecImpliesAlwaysInductiveInvariant ==
  Spec => []InductiveInvariant
PROOF
  BY PTL,
     InitImpliesInductiveInvariant,
     BoxNextPreservesInductiveInvariant
     DEF Spec


THEOREM AlwaysInductiveInvariantImpliesAlwaysSeedStateSafety ==
  []InductiveInvariant => []SeedStateSafety
PROOF
  BY PTL,
     InductiveInvariantImpliesSeedStateSafety


THEOREM SpecImpliesAlwaysSeedStateSafety ==
  Spec => []SeedStateSafety
PROOF
  BY SpecImpliesAlwaysInductiveInvariant,
     AlwaysInductiveInvariantImpliesAlwaysSeedStateSafety


THEOREM RegisterRequestSatisfiesRequestsAppendOnlyStep ==
  ASSUME NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE RequestsAppendOnlyStep
PROOF
  BY DEF RegisterRequest, RequestsAppendOnlyStep


THEOREM SubmitResolutionSatisfiesRequestsAppendOnlyStep ==
  ASSUME NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value)
  PROVE RequestsAppendOnlyStep
PROOF
  BY DEF SubmitResolution, RequestsAppendOnlyStep


THEOREM ObserveConflictSatisfiesRequestsAppendOnlyStep ==
  ASSUME NEW r \in ResolutionIds,
         ObserveConflict(r)
  PROVE RequestsAppendOnlyStep
PROOF
  BY DEF ObserveConflict, RequestsAppendOnlyStep


THEOREM ObserveInvalidMaterialSatisfiesRequestsAppendOnlyStep ==
  ASSUME NEW r \in ResolutionIds,
         ObserveInvalidMaterial(r)
  PROVE RequestsAppendOnlyStep
PROOF
  BY DEF ObserveInvalidMaterial, RequestsAppendOnlyStep


THEOREM ObserveNonAuthoritativeInputSatisfiesRequestsAppendOnlyStep ==
  ASSUME NEW r \in ResolutionIds,
         ObserveNonAuthoritativeInput(r)
  PROVE RequestsAppendOnlyStep
PROOF
  BY DEF ObserveNonAuthoritativeInput, RequestsAppendOnlyStep


THEOREM EvaluateSatisfiesRequestsAppendOnlyStep ==
  Evaluate => RequestsAppendOnlyStep
PROOF
  BY DEF Evaluate, vars, RequestsAppendOnlyStep


THEOREM RecognizedCanonicalTransitionSatisfiesRequestsAppendOnlyStep ==
  RecognizedCanonicalTransition => RequestsAppendOnlyStep
PROOF
  BY RegisterRequestSatisfiesRequestsAppendOnlyStep,
     SubmitResolutionSatisfiesRequestsAppendOnlyStep,
     ObserveConflictSatisfiesRequestsAppendOnlyStep,
     ObserveInvalidMaterialSatisfiesRequestsAppendOnlyStep,
     ObserveNonAuthoritativeInputSatisfiesRequestsAppendOnlyStep
     DEF RecognizedCanonicalTransition


THEOREM NextSatisfiesRequestsAppendOnlyStep ==
  Next => RequestsAppendOnlyStep
PROOF
  BY RecognizedCanonicalTransitionSatisfiesRequestsAppendOnlyStep,
     EvaluateSatisfiesRequestsAppendOnlyStep
     DEF Next


THEOREM BoxNextSatisfiesBoxRequestsAppendOnlyStep ==
  [Next]_vars => [RequestsAppendOnlyStep]_vars
PROOF
  BY NextSatisfiesRequestsAppendOnlyStep
     DEF vars, RequestsAppendOnlyStep


THEOREM SpecImpliesRequestsAppendOnly ==
  Spec => RequestsAppendOnly
PROOF
  BY PTL,
     BoxNextSatisfiesBoxRequestsAppendOnlyStep
     DEF Spec, RequestsAppendOnly


THEOREM RegisterRequestSatisfiesObservedInputsAppendOnlyStep ==
  ASSUME NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE ObservedInputsAppendOnlyStep
PROOF
  BY DEF RegisterRequest, ObservedInputsAppendOnlyStep


THEOREM SubmitResolutionSatisfiesObservedInputsAppendOnlyStep ==
  ASSUME NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value)
  PROVE ObservedInputsAppendOnlyStep
PROOF
  BY DEF SubmitResolution, ObservedInputsAppendOnlyStep


THEOREM ObserveConflictSatisfiesObservedInputsAppendOnlyStep ==
  ASSUME NEW r \in ResolutionIds,
         ObserveConflict(r)
  PROVE ObservedInputsAppendOnlyStep
PROOF
  BY DEF ObserveConflict, ObservedInputsAppendOnlyStep


THEOREM ObserveInvalidMaterialSatisfiesObservedInputsAppendOnlyStep ==
  ASSUME NEW r \in ResolutionIds,
         ObserveInvalidMaterial(r)
  PROVE ObservedInputsAppendOnlyStep
PROOF
  BY DEF ObserveInvalidMaterial, ObservedInputsAppendOnlyStep


THEOREM ObserveNonAuthoritativeInputSatisfiesObservedInputsAppendOnlyStep ==
  ASSUME NEW r \in ResolutionIds,
         ObserveNonAuthoritativeInput(r)
  PROVE ObservedInputsAppendOnlyStep
PROOF
  BY DEF ObserveNonAuthoritativeInput, ObservedInputsAppendOnlyStep


THEOREM EvaluateSatisfiesObservedInputsAppendOnlyStep ==
  Evaluate => ObservedInputsAppendOnlyStep
PROOF
  BY DEF Evaluate, vars, ObservedInputsAppendOnlyStep


THEOREM RecognizedCanonicalTransitionSatisfiesObservedInputsAppendOnlyStep ==
  RecognizedCanonicalTransition => ObservedInputsAppendOnlyStep
PROOF
  BY RegisterRequestSatisfiesObservedInputsAppendOnlyStep,
     SubmitResolutionSatisfiesObservedInputsAppendOnlyStep,
     ObserveConflictSatisfiesObservedInputsAppendOnlyStep,
     ObserveInvalidMaterialSatisfiesObservedInputsAppendOnlyStep,
     ObserveNonAuthoritativeInputSatisfiesObservedInputsAppendOnlyStep
     DEF RecognizedCanonicalTransition


THEOREM NextSatisfiesObservedInputsAppendOnlyStep ==
  Next => ObservedInputsAppendOnlyStep
PROOF
  BY RecognizedCanonicalTransitionSatisfiesObservedInputsAppendOnlyStep,
     EvaluateSatisfiesObservedInputsAppendOnlyStep
     DEF Next


THEOREM BoxNextSatisfiesBoxObservedInputsAppendOnlyStep ==
  [Next]_vars => [ObservedInputsAppendOnlyStep]_vars
PROOF
  BY NextSatisfiesObservedInputsAppendOnlyStep
     DEF vars, ObservedInputsAppendOnlyStep


THEOREM SpecImpliesObservedInputsAppendOnly ==
  Spec => ObservedInputsAppendOnly
PROOF
  BY PTL,
     BoxNextSatisfiesBoxObservedInputsAppendOnlyStep
     DEF Spec, ObservedInputsAppendOnly


THEOREM RegisterRequestSatisfiesTerminalRecordsImmutableStep ==
  ASSUME NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW previous \in ResolutionIds \cup {NoResolution},
         RegisterRequest(r, b, a, previous)
  PROVE TerminalRecordsImmutableStep
PROOF
  BY DEF RegisterRequest, TerminalRecordsImmutableStep


THEOREM SubmitResolutionSatisfiesTerminalRecordsImmutablePointwise ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value),
         NEW p \in ResolutionIds,
         terminalRecord[p] # NoRecord
  PROVE
    /\ terminalRecord'[p] = terminalRecord[p]
    /\ terminalBinding'[p] = terminalBinding[p]
    /\ terminalAuthority'[p] = terminalAuthority[p]
PROOF
  <1>1. terminalRecord[r] = NoRecord
    BY SubmitResolutionGuardFacts

  <1>2. p # r
    BY <1>1

  <1>3. QED
    BY <1>2,
       SubmitResolutionOldKeyValues


THEOREM SubmitResolutionSatisfiesTerminalRecordsImmutableStep ==
  ASSUME InductiveInvariant,
         NEW r \in ResolutionIds,
         NEW b \in Bindings,
         NEW a \in Authorities,
         NEW value \in TerminalResolutions,
         SubmitResolution(r, b, a, value)
  PROVE TerminalRecordsImmutableStep
PROOF
  BY SubmitResolutionSatisfiesTerminalRecordsImmutablePointwise
     DEF TerminalRecordsImmutableStep


THEOREM ObserveConflictSatisfiesTerminalRecordsImmutableStep ==
  ASSUME NEW r \in ResolutionIds,
         ObserveConflict(r)
  PROVE TerminalRecordsImmutableStep
PROOF
  BY DEF ObserveConflict, TerminalRecordsImmutableStep


THEOREM ObserveInvalidMaterialSatisfiesTerminalRecordsImmutableStep ==
  ASSUME NEW r \in ResolutionIds,
         ObserveInvalidMaterial(r)
  PROVE TerminalRecordsImmutableStep
PROOF
  BY DEF ObserveInvalidMaterial, TerminalRecordsImmutableStep


THEOREM ObserveNonAuthoritativeInputSatisfiesTerminalRecordsImmutableStep ==
  ASSUME NEW r \in ResolutionIds,
         ObserveNonAuthoritativeInput(r)
  PROVE TerminalRecordsImmutableStep
PROOF
  BY DEF ObserveNonAuthoritativeInput,
         TerminalRecordsImmutableStep


THEOREM EvaluateSatisfiesTerminalRecordsImmutableStep ==
  Evaluate => TerminalRecordsImmutableStep
PROOF
  BY DEF Evaluate, vars, TerminalRecordsImmutableStep


THEOREM RecognizedCanonicalTransitionSatisfiesTerminalRecordsImmutableStep ==
  InductiveInvariant /\ RecognizedCanonicalTransition
    => TerminalRecordsImmutableStep
PROOF
  BY RegisterRequestSatisfiesTerminalRecordsImmutableStep,
     SubmitResolutionSatisfiesTerminalRecordsImmutableStep,
     ObserveConflictSatisfiesTerminalRecordsImmutableStep,
     ObserveInvalidMaterialSatisfiesTerminalRecordsImmutableStep,
     ObserveNonAuthoritativeInputSatisfiesTerminalRecordsImmutableStep
     DEF RecognizedCanonicalTransition


THEOREM NextSatisfiesTerminalRecordsImmutableStep ==
  InductiveInvariant /\ Next
    => TerminalRecordsImmutableStep
PROOF
  BY RecognizedCanonicalTransitionSatisfiesTerminalRecordsImmutableStep,
     EvaluateSatisfiesTerminalRecordsImmutableStep
     DEF Next


THEOREM BoxNextSatisfiesBoxTerminalRecordsImmutableStep ==
  InductiveInvariant /\ [Next]_vars
    => [TerminalRecordsImmutableStep]_vars
PROOF
  BY NextSatisfiesTerminalRecordsImmutableStep
     DEF vars, TerminalRecordsImmutableStep


THEOREM SpecImpliesTerminalRecordsImmutable ==
  Spec => TerminalRecordsImmutable
PROOF
  BY PTL,
     SpecImpliesAlwaysInductiveInvariant,
     BoxNextSatisfiesBoxTerminalRecordsImmutableStep
     DEF Spec, TerminalRecordsImmutable


THEOREM RecognizedCanonicalTransitionSatisfiesCanonicalTransitionStep ==
  RecognizedCanonicalTransition
    => CanonicalStateChangesOnlyByRecognizedTransitionStep
PROOF
  BY DEF CanonicalStateChangesOnlyByRecognizedTransitionStep


THEOREM EvaluateSatisfiesCanonicalTransitionStep ==
  Evaluate
    => CanonicalStateChangesOnlyByRecognizedTransitionStep
PROOF
  BY DEF Evaluate,
         vars,
         canonicalVars,
         CanonicalStateChangesOnlyByRecognizedTransitionStep


THEOREM NextSatisfiesCanonicalTransitionStep ==
  Next
    => CanonicalStateChangesOnlyByRecognizedTransitionStep
PROOF
  BY RecognizedCanonicalTransitionSatisfiesCanonicalTransitionStep,
     EvaluateSatisfiesCanonicalTransitionStep
     DEF Next


THEOREM BoxNextSatisfiesBoxCanonicalTransitionStep ==
  [Next]_vars
    => [CanonicalStateChangesOnlyByRecognizedTransitionStep]_vars
PROOF
  BY NextSatisfiesCanonicalTransitionStep
     DEF vars,
         canonicalVars,
         CanonicalStateChangesOnlyByRecognizedTransitionStep


THEOREM SpecImpliesCanonicalStateChangesOnlyByRecognizedTransition ==
  Spec => CanonicalStateChangesOnlyByRecognizedTransition
PROOF
  BY PTL,
     BoxNextSatisfiesBoxCanonicalTransitionStep
     DEF Spec,
         CanonicalStateChangesOnlyByRecognizedTransition

=============================================================================
