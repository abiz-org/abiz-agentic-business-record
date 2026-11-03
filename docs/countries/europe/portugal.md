# Tornar-se uma empresa agêntica com o ABIZ em Portugal

*Guia do ABIZ 1.1 (proposta). O texto de referência é a [especificação (SPEC.md, em inglês)](../../../SPEC.md): se este guia e a especificação divergirem, prevalece a especificação.*

## 1. O que isto significa para uma empresa em Portugal

Cada vez mais pessoas perguntam a assistentes de IA sobre empresas: quem são, o que oferecem, onde as encontrar. Com o ABIZ (Agentic Business Record), uma empresa publica um registo público e legível por máquinas com os seus próprios dados, como nome, país, site, serviços e horário, e, no seu próprio domínio, um registo DNS que aponta para esse registo.

Só a empresa, ou quem atue em seu nome, pode alterar o DNS do seu domínio. Assim, um software compatível consegue encontrar o registo a partir do domínio e verificar que o domínio e o registo remetem um para o outro, em vez de juntar dados de páginas web dispersas. O ABIZ é aberto e independente de fornecedores: não exige adesão, taxas nem um fornecedor específico.

## 2. Como publicar um registo ABIZ

### Campos obrigatórios

O registo da empresa é um documento JSON que tem de cumprir o [esquema normativo](../../../schemas/abiz-business-record-v1.schema.json). Há cinco campos obrigatórios:

| Campo | Exemplo | Notas |
| --- | --- | --- |
| `record_version` | `abiz1` | Sempre este valor |
| `business_name` | `Pastelaria Ribeira Lda` | O nome público, normalmente como consta do registo comercial, com a forma jurídica se a usar |
| `country` | `pt` | Código de país ISO 3166-1 alfa-2; a forma canónica é em minúsculas |
| `identity_host` | `pastelariaribeira.pt.to.co` | Exatamente o valor DNS `h`: um nome de anfitrião com caminho opcional, sem `https://` |
| `domains` | `["pastelariaribeira.example"]` | Os domínios reivindicados pelo registo, incluindo o que tem `_abiz` |

### Chave de empresa `k` (opcional)

`k` é opcional para qualquer empresa, registada ou não. Se o publicar, o registo tem de incluir também `business_key` e `registration_number`, e `k` tem de ser igual a `business_key`.

Em Portugal a chave é `pt-` seguido do número, sem subdivisão territorial: uma chave com uma parte intermédia, como `pt-xx-…`, é inválida.

- **Registo:** registo comercial, a cargo do [Instituto dos Registos e do Notariado (IRN)](https://irn.justica.gov.pt/)
- **Número a usar:** o NIPC (número de identificação de pessoa coletiva), de 9 algarismos, que é também o número de matrícula no registo comercial
- **Como o escrever:** parta do número tal como é atribuído, aplique a normalização Unicode NFKC, retire espaços, `-`, `.`, `/` e outros hífenes e escreva as letras em maiúsculas. Os zeros à esquerda e os prefixos em letras mantêm-se. O resultado só pode conter letras e algarismos ASCII.

Exemplo (número inventado): `512 345 678` passa a `512345678`. O registo contém então `"registration_number": "512345678"` e `"business_key": "pt-512345678"`, e o DNS indica `k=pt-512345678`. Não use o prefixo `PT` do número de IVA.

As chaves comparam-se sem distinguir maiúsculas de minúsculas, mas publique a forma canónica: código do país em minúsculas e número em maiúsculas.

### Registo DNS TXT

Publique um único registo TXT ABIZ em `_abiz` no seu domínio, na forma compacta e sem espaços:

```dns
_abiz.pastelariaribeira.example. 300 IN TXT "v=abiz1;k=pt-512345678;h=pastelariaribeira.pt.to.co;p=NRD9R/v55ek3v710riRR0Tf+0kn0hG71JVC2OYc6nw0="
```

- `v=abiz1` tem de vir primeiro. `h` é obrigatório; `k` e `p` são opcionais.
- Os nomes das etiquetas são em minúsculas e distinguem maiúsculas de minúsculas. Nenhuma etiqueta pode repetir-se.
- Recomenda-se um TTL de 300 segundos.

O valor `p` acima é uma chave de exemplo descartável. Nunca a copie: publique a sua própria chave ou omita `p`.

### Registo da empresa (JSON)

O registo disponibilizado em `https://pastelariaribeira.pt.to.co` como `application/json`:

```json
{
  "record_version": "abiz1",
  "business_name": "Pastelaria Ribeira Lda",
  "country": "pt",
  "business_key": "pt-512345678",
  "registration_number": "512345678",
  "identity_host": "pastelariaribeira.pt.to.co",
  "domains": [
    "pastelariaribeira.example"
  ],
  "public_key": "NRD9R/v55ek3v710riRR0Tf+0kn0hG71JVC2OYc6nw0=",
  "description": "Pastelaria no Porto.",
  "website": "https://pastelariaribeira.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Porto",
        "country": {
          "code": "PT"
        }
      },
      "public": true
    }
  ],
  "signature": "Bgl/ANNlyZ6zQoAq9QbsEZMoLqiRm8vvdSIkIl/EMrDwQG3mciAPZKy4Kl58e71VdXuPQiJvHdMW5j6Y9Qh7DA=="
}
```

Com o validador de referência pode verificar localmente o registo e o valor DNS:

```sh
python scripts/validate.py record.json --domain pastelariaribeira.example --dns-value 'v=abiz1;k=pt-512345678;h=pastelariaribeira.pt.to.co;p=NRD9R/v55ek3v710riRR0Tf+0kn0hG71JVC2OYc6nw0='
```

### Alojamento próprio ou através de um fornecedor

Pode disponibilizar o registo em qualquer anfitrião HTTPS que controle ou usar qualquer fornecedor compatível. O ABIZ não impõe fornecedor nem esquema de nomes. Em qualquer caso, o registo tem de ser servido por HTTPS e tem de controlar o domínio que tem `_abiz`.

## 3. Fornecedores e MCP

O MCP (Model Context Protocol) é um protocolo aberto que permite aos assistentes de IA chamar ferramentas e ler dados de servidores externos. Um fornecedor pode gerir um servidor MCP através do qual um assistente obtém diretamente o seu registo público. Pode indicá-lo no campo opcional `mcp_server_url`. O ABIZ não exige um servidor MCP, e uma ferramenta não deve chamá-lo automaticamente só porque consta de um registo.

Por exemplo, um fornecedor pode disponibilizar o seu registo em `pastelariaribeira.pt.to.co` e gerir um servidor MCP. Um assistente ligado a esse servidor pode então perguntar pelo horário ou pelos serviços da Pastelaria Ribeira Lda e receber os dados do seu registo, em vez de os adivinhar. A to.co, um desses fornecedores, explica o ABIZ numa [página em português](https://to.co/pt-pt/abiz).

## 4. Chaves e assinaturas (ABIZ 1.1)

O ABIZ 1.1 permite publicar uma chave pública Ed25519 na etiqueta DNS `p`. `p` é opcional. Se existir, tem de ser a codificação base64 padrão da chave de 32 bytes: 44 caracteres terminados num único `=`, numa só cadeia DNS. Qualquer outro valor, como um token hexadecimal do ABIZ 1.0 ou uma chave em base64url, invalida todo o registo.

A chave privada correspondente pertence à empresa e nunca é publicada. Se um fornecedor a guardar por si, tem de lhe permitir exportá-la. Um software pode verificar uma assinatura feita com a chave privada usando a chave publicada no DNS. O ABIZ 1.1 ainda não define que bytes uma assinatura do registo abrange.

Para mudar de chave, publique uma nova em `p`; para a revogar, retire `p`. No ABIZ 1.1 as chaves retiradas não são publicadas, nem no DNS nem no registo. A chave mostra que chave publicou quem controla o domínio; não prova a identidade jurídica.

## 5. O que as ferramentas de IA veem

Com um registo válido, um assistente compatível pode responder a perguntas como:

- «A Pastelaria Ribeira Lda é uma empresa do Porto?»
- «O que oferece a Pastelaria Ribeira Lda e qual é o horário?»
- «pastelariaribeira.example é o site oficial da Pastelaria Ribeira Lda?»
- «Que número de identificação declara a Pastelaria Ribeira Lda?»

Os limites importam. O ABIZ mostra que um domínio e um registo remetem um para o outro. Não prova que a empresa esteja legalmente registada, que um número seja autêntico nem que alguém a recomende. Uma ferramenta que não tenha consultado ela própria o registo comercial não deve apresentar a empresa como verificada. O ABIZ não garante que um serviço de IA encontre, classifique ou recomende uma empresa.

## 6. Notas práticas

### Onde encontrar o número

O NIPC consta do cartão da empresa, da certidão permanente e das faturas. Os serviços de registo estão descritos no [IRN](https://irn.justica.gov.pt/) e no portal [ePortugal](https://eportugal.gov.pt/). O NIF de um empresário em nome individual é o seu número pessoal: nesse caso não publique a chave, porque identifica uma pessoa.

### Adicionar o registo TXT

Adicione o registo onde é gerido o DNS do seu domínio, normalmente no seu registrar ou alojamento. O registo dos domínios `.pt` é o [.PT](https://www.pt.pt/), mas o registo TXT adiciona-se no seu registrar ou fornecedor de DNS; serve qualquer um que suporte registos TXT. Crie um registo do tipo TXT com o nome `_abiz` (alguns painéis pedem o nome completo, `_abiz.pastelariaribeira.example`), o valor exatamente como acima e um TTL de 300. Não acrescente espaços ao valor e remova registos ABIZ antigos, para que fique apenas um.

### Privacidade e publicação de dados

O RGPD aplica-se aos dados pessoais do registo, por exemplo o nome de um empresário em nome individual ou de uma pessoa de contacto. O [Comité Europeu para a Proteção de Dados](https://www.edpb.europa.eu/) indica as autoridades nacionais; em Portugal é a Comissão Nacional de Proteção de Dados (CNPD). Tudo o que está num registo ABIZ é público: publique apenas dados que queira tornar públicos. Um empresário em nome individual não deve publicar a morada de casa: a especificação exige que as moradas pessoais sejam omitidas, e não marcadas como privadas. Um endereço genérico como `geral@` é melhor do que um e-mail pessoal.

## 7. Saber mais

- [Especificação ABIZ (SPEC.md, em inglês)](../../../SPEC.md): sintaxe DNS (secção 3.1.1), chave `p` (secção 3.3), chaves de empresa (secção 4.2)
- [Esquema JSON normativo](../../../schemas/abiz-business-record-v1.schema.json)
- [Validador de referência, scripts/validate.py](../../../scripts/validate.py)
- [Todos os guias da Europa](index.md)
