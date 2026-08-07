[English](README.md) · [Русский](README.ru.md) · [Português do Brasil](README.pt-BR.md)

# ASET

ASET é uma especificação aberta e neutra de implementação para Authority-Signed Evidence Trails. Seu Seed é um núcleo mínimo local de reconhecimento de resolução.

```text
UNKNOWN | ALLOW | BLOCK
```

Somente um registro `ALLOW` único, válido, localmente autorizado e exatamente vinculado permite o efeito vinculado. A ausência de estado terminal válido ou o conflito entre registros terminais válidos resulta em `UNKNOWN`; proibição explícita é `BLOCK`. Material inválido ou não autoritativo não pode substituir um registro terminal válido que, de outro modo, seria único. Evidence, saída de AI e outcome remoto não criam Authority local por si só.

Repository boundary records: [EXTRACTION.md](EXTRACTION.md), [IMPLEMENTATIONS.md](IMPLEMENTATIONS.md), [EXTENSIONS.md](EXTENSIONS.md).

Background IP: [BACKGROUND_IP_SCHEDULE.md](BACKGROUND_IP_SCHEDULE.md).
