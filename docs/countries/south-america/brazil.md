# Tornar-se uma empresa agêntica com ABIZ no Brasil

*Guia da especificação publicada ABIZ 1.1. O [SPEC.md](../../../SPEC.md) é o texto de referência: se este guia e a especificação divergirem, vale a especificação.*

## 1. O que isso significa para uma empresa no Brasil

Cada vez mais pessoas fazem a assistentes de IA perguntas como “qual padaria perto de mim abre no domingo?” ou “este site pertence mesmo a esta empresa?”. A ABIZ (Agentic Business Record) é um padrão aberto que permite a uma empresa publicar seus dados públicos de forma que softwares compatíveis possam encontrá-los e verificá-los: um pequeno documento JSON com esses dados e um registro DNS TXT, no domínio da própria empresa, que aponta para ele.

Com a ABIZ, um assistente compatível pode partir do seu domínio, encontrar o seu registro, validá-lo com o JSON Schema publicado e confirmar que o domínio e o registro apontam um para o outro. Serve tanto para empresas registradas quanto para negócios sem registro. A ABIZ não garante que algum assistente vá encontrar, classificar ou recomendar a sua empresa, e não é um selo oficial.

No Brasil, uma empresa pode usar o CNPJ como chave empresarial; um negócio sem CNPJ pode publicar o registro sem chave.

## 2. Como publicar um registro ABIZ

### Campos obrigatórios

| Campo | O que colocar | Exemplo |
| --- | --- | --- |
| `record_version` | Sempre `abiz1` | `abiz1` |
| `business_name` | O nome público da empresa | `Padaria Pão de Mel Ltda.` |
| `country` | O código de país ISO 3166-1 alfa-2, em minúsculas | `br` |
| `identity_host` | O host, com caminho opcional, onde o registro é servido; deve coincidir com `h` no DNS | `padariapaodemel.br.to.co` |
| `domains` | Os domínios que você controla e que o registro reivindica | `["padariapaodemel.example"]` |

### A chave empresarial opcional `k`

`k` é opcional para qualquer empresa. Se você publicá-la, ela deve seguir a seção 4.2 da especificação e ser igual ao `business_key` do registro. Maiúsculas e minúsculas não importam na comparação, mas a forma canônica tem o código do país em minúsculas e o número de registro em maiúsculas.

Formato: `br-` seguido do CNPJ de 14 caracteres, sem pontuação (seção 4.2.2). Não há código de estado: embora as empresas sejam registradas nas Juntas Comerciais estaduais, o CNPJ emitido pela Receita Federal é nacional e único. O [CNPJ alfanumérico](https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/acoes-e-programas/programas-e-atividades/cnpj-alfanumerico) já se encaixa na gramática: as letras ficam em maiúsculas. A especificação não trata de filiais; como cada empresa tem uma única chave, recomendamos usar o CNPJ da matriz (final `/0001-`). Quem trabalha por conta própria e só tem CPF não deve publicar `k`: o CPF é um número pessoal, e a especificação prevê apenas o CNPJ.

**Normalização do número (seção 4.2.3).** Parta do número exatamente como o órgão de registro o emite. Aplique a normalização Unicode NFKC; remova espaços, hífens, pontos e barras; converta as letras para maiúsculas; mantenha zeros à esquerda e prefixos de letras. Se sobrar qualquer outro caractere, como parênteses, `&` ou uma letra acentuada, o número não pode ser expresso e você não pode publicar uma chave empresarial: omita `k`, `business_key` e `registration_number`.

**Exemplo (fictício):** o CNPJ `12.345.678/0001-95` vira `12345678000195`, e a chave é `br-12345678000195`.

Se incluir `business_key` e `registration_number` no registro, inclua os dois, e a parte numérica da chave deve ser igual a `registration_number`. Incluí-los não obriga você a publicar `k` no DNS. Se publicar `k`, o registro precisa conter o `business_key` correspondente.

### O registro DNS TXT

Publique exatamente um registro TXT que comece com `v=abiz1` em `_abiz.` seguido do seu domínio. Use a forma compacta, sem espaços (seção 3.1.1), e um TTL de 300 segundos:

```dns
_abiz.padariapaodemel.example. 300 IN TXT "v=abiz1;k=br-12345678000195;h=padariapaodemel.br.to.co;p=niKc1zneSrFY7FSaVPdGpN1X4okFDQFxJNQI7OULqaw="
```

Uma empresa sem número de registro, ou que prefira não publicá-lo, simplesmente omite `k`:

```dns
_abiz.bancadafeira.example. 300 IN TXT "v=abiz1;h=bancadafeira.biz.to.co"
```

### Exemplo de registro (JSON)

Este exemplo é fictício. Ele passa no validador de referência.

```json
{
  "record_version": "abiz1",
  "business_name": "Padaria Pão de Mel Ltda.",
  "country": "br",
  "business_key": "br-12345678000195",
  "registration_number": "12345678000195",
  "identity_host": "padariapaodemel.br.to.co",
  "domains": [
    "padariapaodemel.example"
  ],
  "public_key": "niKc1zneSrFY7FSaVPdGpN1X4okFDQFxJNQI7OULqaw=",
  "description": "Padaria artesanal no bairro de Pinheiros.",
  "website": "https://padariapaodemel.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "São Paulo",
        "region": {
          "code": "BR-SP",
          "name": "São Paulo"
        },
        "country": {
          "code": "BR"
        }
      },
      "opening_hours": {
        "time_zone": "America/Sao_Paulo",
        "weekly": [
          {
            "day": "monday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "20:00"
              }
            ]
          },
          {
            "day": "tuesday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "20:00"
              }
            ]
          },
          {
            "day": "wednesday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "20:00"
              }
            ]
          },
          {
            "day": "thursday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "20:00"
              }
            ]
          },
          {
            "day": "friday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "20:00"
              }
            ]
          },
          {
            "day": "saturday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "20:00"
              }
            ]
          },
          {
            "day": "sunday",
            "periods": [
              {
                "opens": "07:00",
                "closes": "13:00"
              }
            ]
          }
        ]
      },
      "public": true
    }
  ],
  "signature": "Uvv94nEZZt/UXrCavZRlibG/0v4n1k9517OK1dudBCgv7DleMAbudcxPtGtc6GNirQ08cifrEyiRfvYH4a10Dg=="
}
```

### Onde o registro fica hospedado

Você pode servir o registro por conta própria a partir de qualquer URL HTTPS que retorne o documento JSON, por exemplo `h=www.padariapaodemel.example/abiz.json`, ou usar qualquer provedor compatível. A ABIZ não exige um provedor nem um padrão de nomes específico. Seja qual for a escolha, o `identity_host` do registro deve coincidir com `h`, e `domains` deve incluir o domínio onde você publica o registro TXT.

Antes de publicar, verifique o registro e o valor DNS com o validador de referência:

```sh
python scripts/validate.py record.json \
  --domain padariapaodemel.example \
  --dns-value 'v=abiz1;k=br-12345678000195;h=padariapaodemel.br.to.co;p=niKc1zneSrFY7FSaVPdGpN1X4okFDQFxJNQI7OULqaw='
```

## 3. Provedores e MCP

O Model Context Protocol (MCP) é um protocolo aberto que permite que assistentes de IA usem ferramentas e leiam dados de serviços externos de forma padronizada. Um registro ABIZ pode incluir um `mcp_server_url` opcional: o endereço HTTPS de um servidor MCP que responda a perguntas sobre a empresa, como horários, serviços ou disponibilidade. A ABIZ não exige um servidor MCP, e o fato de ele constar no registro não é uma garantia: um software compatível não deve chamá-lo automaticamente só porque ele aparece num registro, e deve aplicar os próprios controles de acesso.

Por exemplo, um provedor pode hospedar o registro da Padaria Pão de Mel em `padariapaodemel.br.to.co`, publicar o registro DNS TXT pelo seu próprio processo de configuração e indicar o seu servidor MCP em `mcp_server_url`. Você pode trocar de provedor, ou passar a hospedar o registro por conta própria, alterando `h` e o `identity_host` do registro.

## 4. Chaves e assinaturas (ABIZ 1.1)

- **`p` é obrigatória.** `v` e `h` são obrigatórios; `k` é opcional. `p` deve ser uma chave pública Ed25519: 32 bytes brutos, base64 padrão, exatamente 44 caracteres, um único `=` no fim. Base64url não é aceito (seção 3.3.2). Qualquer outro valor, como um antigo token hexadecimal da ABIZ 1.0, invalida toda a declaração.
- **Exemplo** (a chave é um exemplo descartável; a chave privada correspondente foi descartada). Nunca a copie: publique a sua própria chave. Uma asserção ABIZ 1.1 tem de incluir `p`.

  ```dns
  _abiz.padariapaodemel.example. 300 IN TXT "v=abiz1;k=br-12345678000195;h=padariapaodemel.br.to.co;p=niKc1zneSrFY7FSaVPdGpN1X4okFDQFxJNQI7OULqaw="
  ```

- **A chave privada pertence à empresa.** Ela nunca deve aparecer no DNS, no registro nem num repositório público. Um provedor pode gerá-la e guardá-la por você (modo hospedado), mas deve permitir que você a exporte a qualquer momento, por exemplo em PKCS#8, e apagar a cópia dele quando você pedir (seção 3.3.4).
- **Assinaturas.** Um software pode verificar uma assinatura Ed25519 destacada com a chave publicada. A assinatura do registro cobre a forma canônica RFC 8785 do registro sem o membro `signature` e é verificada com `public_key`, que deve ser igual a `p` (SPEC seção 4.6). Uma assinatura sobre outra mensagem só faz sentido se as duas partes tiverem combinado essa mensagem.
- **Rotação e chaves aposentadas.** Para trocar de chave, publique a nova em `p`; a antiga deixa de ser a vigente depois que o TTL do registro TXT expira. A ABIZ 1.1 não publica chaves aposentadas: nem no DNS, nem no registro (uma propriedade `retired_keys` é rejeitada).
- **O que uma chave prova.** Ela mostra qual chave quem controla o domínio publicou. Ela não assina, por si só, o registro TXT e não prova identidade jurídica. Use DNSSEC se o seu provedor de DNS oferecer.

## 5. O que as ferramentas de IA vão ver

Um software compatível que leia o seu registro pode responder a perguntas como:

- “A Padaria Pão de Mel abre no domingo?”
- “Quais produtos a Padaria Pão de Mel vende em São Paulo?”
- “Qual é o site oficial da Padaria Pão de Mel?”
- “Qual é o CNPJ publicado pela Padaria Pão de Mel?”

Ele também pode informar que o domínio e o registro apontam um para o outro, que o registro atende ao schema e se há uma chave `p` válida publicada.

**Limites.** Um registro ABIZ não é prova de registro legal. Uma ferramenta só pode apresentar uma empresa como confirmada no registro oficial se tiver consultado esse registro separadamente e indicar isso. A ABIZ não é um aval, nem um selo de qualidade, nem uma promessa de visibilidade em qualquer serviço de IA.

## 6. Observações práticas locais

**Número de registro.** O CNPJ consta do comprovante de inscrição emitido pela [Receita Federal](https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/cadastros/cnpj). O NIRE da Junta Comercial é estadual e não é usado na chave.

**Como adicionar o registro TXT.** Entre no painel onde o DNS do seu domínio é gerenciado: normalmente a empresa onde você registrou o domínio ou o seu provedor de hospedagem. Adicione um registro do tipo TXT com o nome `_abiz` (alguns painéis pedem o nome completo, `_abiz.padariapaodemel.example`), cole o valor sem as aspas e, se o painel permitir, defina o TTL em 300 segundos. Domínios `.br` são registrados no [Registro.br](https://registro.br/), que também oferece DNS.

**Privacidade.** O registro e o valor TXT são públicos. Publique apenas dados que você quer tornar públicos. Quem trabalha por conta própria não deve publicar o endereço residencial nem o telefone pessoal; é melhor omitir um campo do que marcá-lo como privado (seção 4.3). No Brasil, aplica-se a Lei Geral de Proteção de Dados (LGPD, Lei 13.709/2018), fiscalizada pela [ANPD](https://www.gov.br/anpd/pt-br). Um MEI deve pensar bem antes de publicar dados que identifiquem a pessoa física.

## 7. Para saber mais

- [Especificação da ABIZ](../../../SPEC.md) (em inglês): seção 3.1.1 (sintaxe TXT), seção 3.3 (chaves `p`), seção 4.2 (chaves empresariais)
- [JSON Schema do registro](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Validador de referência](../../../scripts/validate.py) e [exemplos](../../../examples/)
- [Todos os guias da América do Sul](index.md)
