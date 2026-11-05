# Tornar-se uma empresa agêntica com o ABIZ em São Tomé e Príncipe

*Guia para a especificação publicada ABIZ 1.1. A [especificação (SPEC.md, em inglês)](../../../SPEC.md) é o texto de referência: se este guia e a especificação divergirem, aplica-se a especificação.* O português é a língua oficial e a língua dos negócios.

## 1. O que isto significa para uma empresa em São Tomé e Príncipe

Os assistentes de IA recebem cada vez mais perguntas como «qual é o verdadeiro site desta empresa?» ou «quem explora esta loja?». O ABIZ (Agentic Business Record) é uma norma aberta que permite a uma empresa em São Tomé e Príncipe publicar uma única vez os seus dados públicos, numa forma que essas ferramentas sabem ler: um pequeno registo DNS TXT num domínio que a empresa controla, que aponta para uma ficha de empresa em JSON servida por HTTPS. Como esse ponteiro está no DNS da própria empresa, uma ferramenta consegue verificar que a ficha foi publicada por quem controla o domínio, em vez de depender de um diretório não oficial ou de uma suposição.

## 2. Como publicar um registo ABIZ

### Campos obrigatórios

Todas as fichas de empresa têm estes cinco campos (secção 4.1 da SPEC):

| Campo | Exemplo e regra |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | o nome público que os clientes conhecem, por exemplo `Chocolates do Equador` |
| `country` | `st`, o código ISO 3166-1 alfa-2, em minúsculas |
| `identity_host` | `chocolatesequador.st.to.co`, que tem de coincidir exatamente com `h` no DNS |
| `domains` | `["chocolatesequador.example"]`, que tem de incluir o domínio onde está `_abiz` |

### Chave de empresa opcional `k`

A `k` é opcional para qualquer empresa, registada ou não. Se a publicar, tem de ser igual ao campo `business_key` da ficha, que nesse caso também tem de conter `registration_number`. Para São Tomé e Príncipe, a forma é:

```text
st-<registration-number>
```

São Tomé e Príncipe não usa subdivisão: não acrescente código de região, província ou cidade. A secção 4.2.2 da SPEC só exige subdivisão para os Estados Unidos, as sociedades provinciais do Canadá e os Emirados Árabes Unidos, e proíbe-a em todos os outros países.

**Que número:** o NIF (Número de Identificação Fiscal) da empresa, atribuído a nível nacional.

**Normalização (secção 4.2.3 da SPEC):** parta do número tal como o registo o emite, aplique a normalização Unicode NFKC, retire espaços, `-`, `.`, `/` e travessões, e passe as letras a maiúsculas. Mantenha os zeros à esquerda e os prefixos em letras. O resultado só pode ter letras e algarismos ASCII. Caso contrário, não é possível publicar uma chave de empresa: omita `k`, `business_key` e `registration_number`.

**Exemplo (fictício):** `123456789` passa a `123456789`, logo `k=st-123456789`. Na ficha: `"business_key": "st-123456789"` e `"registration_number": "123456789"`. As chaves comparam-se sem distinguir maiúsculas de minúsculas; a forma canónica tem o código do país em minúsculas e o número em maiúsculas.

**Confirme:** não conseguimos confirmar o formato exato deste número numa fonte oficial, pelo que o exemplo é apenas ilustrativo. Use o número tal como consta do seu documento oficial de registo. Se não for claro qual o número que identifica a empresa a nível nacional, não publique `k` até ter a certeza.

**Empresários em nome individual:** se o único número que tem é pessoal, como o número do bilhete de identidade ou um número fiscal pessoal, não publique `k`. Omita `k`, `business_key` e `registration_number`; o registo continua válido.

### Registo DNS TXT

Publique um único registo TXT em `_abiz` sob o seu domínio, na forma compacta, sem espaços e com `v=abiz1` em primeiro lugar:

```dns
_abiz.chocolatesequador.example. 300 IN TXT "v=abiz1;k=st-123456789;h=chocolatesequador.st.to.co;p=Qwz5AnH64IFkGIRmQsqwnCYTbKIUmLTzrUl0uGWD88s="
```

O valor `p` acima é uma chave de exemplo descartável, gerada para esta página. Nunca a copie: publique a sua própria chave. Uma asserção ABIZ 1.1 tem de incluir `p`. Todos os nomes, números e domínios desta página são fictícios.

Sem as etiquetas opcionais `k` e `p`, isto também é válido:

```dns
_abiz.chocolatesequador.example. 300 IN TXT "v=abiz1;h=chocolatesequador.st.to.co;p=Qwz5AnH64IFkGIRmQsqwnCYTbKIUmLTzrUl0uGWD88s="
```

O registo da empresa servido como `application/json` em `https://chocolatesequador.st.to.co`:

```json
{
  "record_version": "abiz1",
  "business_name": "Chocolates do Equador",
  "country": {
    "code": "ST",
    "name": "S\u00e3o Tom\u00e9 and Pr\u00edncipe"
  },
  "business_key": "st-123456789",
  "registration_number": "123456789",
  "identity_host": "chocolatesequador.st.to.co",
  "domains": [
    "chocolatesequador.example"
  ],
  "public_key": "Qwz5AnH64IFkGIRmQsqwnCYTbKIUmLTzrUl0uGWD88s=",
  "signature": "wUF7PnEMKysKqR2VdcMO6w+RzOdnf43bNIU9hz+xRDdk+/Ie3rRfl3uHpsy7vbzgesjXjoyucShvQ8zS+5aaAA=="
}
```

Para verificar uma ficha antes de a publicar, execute o validador de referência a partir de uma cópia deste repositório:

```sh
python scripts/validate.py record.json --domain chocolatesequador.example --dns-value 'v=abiz1;k=st-123456789;h=chocolatesequador.st.to.co;p=Qwz5AnH64IFkGIRmQsqwnCYTbKIUmLTzrUl0uGWD88s='
```

Pode alojar a ficha JSON por conta própria, em qualquer servidor HTTPS, ou recorrer a qualquer fornecedor compatível. O ABIZ não exige um fornecedor específico.

## 3. Usar um fornecedor e o MCP

O Model Context Protocol (MCP) é um protocolo aberto que permite aos assistentes de IA chamar ferramentas e ler dados de servidores externos de forma normalizada. Uma ficha pode incluir o campo opcional `mcp_server_url`, o endereço HTTPS de um servidor MCP da empresa, por exemplo para reservas ou informação sobre produtos. O ABIZ não garante esse servidor: as ferramentas têm de aplicar os seus próprios controlos de acesso (secção 4.2.6 da SPEC).

Um fornecedor pode alojar a ficha e publicar o ponteiro DNS por si. Por exemplo, uma sociedade registada em São Tomé e Príncipe com a ficha alojada no to.co poderia usar o anfitrião `chocolatesequador.st.to.co`, o que dá o valor DNS `v=abiz1;k=st-123456789;h=chocolatesequador.st.to.co;p=Qwz5AnH64IFkGIRmQsqwnCYTbKIUmLTzrUl0uGWD88s=`. Uma empresa não registada poderia usar um anfitrião baseado na localidade, como `chocolatesequador-saotome.biz.to.co`. Qualquer fornecedor compatível, ou o seu próprio servidor, funciona da mesma maneira.

## 4. Chaves e assinaturas (ABIZ 1.1)

O ABIZ 1.1 exige uma chave de assinatura. A etiqueta DNS `p` contém uma chave pública Ed25519: 32 bytes em bruto, base64 padrão, 44 caracteres, um único `=` final (secção 3.3.2 da SPEC). Base64url não é aceite. A empresa, ou um fornecedor em seu nome, guarda a chave privada correspondente e assina a ficha com ela. A chave privada pertence sempre à empresa, e um fornecedor de alojamento tem de permitir que a exporte.

- `v` e `h` são obrigatórios. `p` é obrigatória. `k` é opcional. `p` tem de ser uma chave válida: qualquer outro valor, como uma sequência hexadecimal ou uma chave em base64url, torna toda a asserção inválida.
- Só se publica a chave atual. Para a substituir, gere um novo par de chaves Ed25519, publique a nova chave pública em `p` na asserção DNS ou well-known, volte a assinar a ficha com a nova chave privada e faça com que `public_key` seja esse mesmo `p`. Tenha em conta a cache e a propagação do DNS. Retirar apenas `p` não é uma revogação válida enquanto a asserção ABIZ 1.1 se mantiver: para a retirar, elimine a declaração DNS ou well-known completa. As chaves retiradas não são publicadas no ABIZ 1.1, nem no DNS, nem na ficha.
- Uma chave mostra quem controla o DNS do domínio. Não prova a identidade jurídica.

## 5. O que as ferramentas de IA vão ver

Uma ferramenta compatível que leia a sua ficha consegue responder a perguntas como:

1. Qual é o site oficial de Chocolates do Equador?
2. Que domínios pertencem a esta empresa?
3. Que número de registo indica a empresa, e em que país?
4. O que oferece, e qual é o horário?

**Limites:** o ABIZ mostra o que o titular de um domínio publicou. Não prova que a empresa está legalmente registada, que o número é autêntico, nem que um serviço de IA, uma entidade pública ou um fornecedor a recomenda. Quando for importante, ferramentas e pessoas devem consultar o registo oficial.

## 6. Notas práticas locais

- **Registo:** Guiché Único para Empresas, que trata do registo comercial. Não indicamos um site porque não conseguimos confirmar um endereço oficial que funcione.
- **Acrescentar o registo TXT:** nas definições DNS do seu registador ou fornecedor de DNS, acrescente um registo TXT com o nome `_abiz` (alguns painéis pedem o nome completo, `_abiz.oseudominio.st`), o valor acima e um TTL de 300 segundos. Os domínios `.st` funcionam como `.com` ou qualquer outro domínio. Mantenha o valor inteiro sempre que possível e nunca divida `p`.
- **Proteção de dados:** Verifique as regras de proteção de dados aplicáveis em São Tomé e Príncipe antes de publicar dados pessoais. Uma ficha ABIZ é pública. Publique apenas informação empresarial que aceite partilhar e omita moradas pessoais e números de telefone privados (secção 4.3 da SPEC).

## 7. Leitura adicional

- [Especificação ABIZ (SPEC.md, em inglês)](../../../SPEC.md)
- [Esquema JSON da ficha de empresa](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Validador de referência](../../../scripts/validate.py)
- [Guias ABIZ por país: África](index.md)
