# Language and terminology policy

## Supported official editions

- Russian: `ru`
- English: `en`
- Brazilian Portuguese: `pt-BR`

Each edition is generated directly from the canonical source.
No language edition is translated from another edition.

## Native-term rule

A foreign term may be used only when no exact, established and
non-misleading native term exists.

Protocol identifiers, source-code symbols, schema property names,
transition kinds and cryptographic identifiers remain unchanged.

## Russian

Prefer:

- `пространство имён`, not `неймспейс`;
- `автомат состояний`, not `стейт-машина`;
- `рабочий процесс`, not `воркфлоу`;
- `фиксация версии`, not `фриз`;
- `носитель полномочия`, not `холдер`.

## Brazilian Portuguese

Prefer:

- `espaço de nomes`, not `namespace`;
- `máquina de estados`, not `state machine`;
- `fluxo de trabalho`, not `workflow`;
- `fixação da versão`, not `freeze`;
- `titular da autoridade`, not `holder`.

## Release review

Automated checks are mandatory for every change.
Human editorial approval in all three languages is mandatory
before a documentation freeze.
