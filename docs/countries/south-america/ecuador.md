# Convertirse en un negocio agéntico con ABIZ en Ecuador

*Guía de la especificación publicada ABIZ 1.1. [SPEC.md](../../../SPEC.md) es el texto de referencia: si esta guía y la especificación difieren, prevalece la especificación.*

## 1. Qué significa para una empresa en Ecuador

Cada vez más personas preguntan a los asistentes de IA cosas como «¿qué panadería cerca de mí abre el domingo?» o «¿este sitio web es de verdad de esta empresa?». ABIZ (Agentic Business Record) es un estándar abierto que permite a un negocio publicar sus datos públicos de forma que el software compatible pueda encontrarlos y comprobarlos: un pequeño documento JSON con esos datos y un registro DNS TXT en el dominio propio del negocio que apunta a él.

Con ABIZ, un asistente compatible puede partir de su dominio, encontrar su registro, validarlo con el JSON Schema publicado y confirmar que el dominio y el registro se refieren el uno al otro. Sirve tanto para empresas inscritas como para negocios sin inscripción. No garantiza que ningún asistente le encuentre, le posicione o le recomiende, y no es un sello oficial.

En Ecuador, una compañía sujeta a la Superintendencia de Compañías, Valores y Seguros puede añadir su número de expediente como clave de empresa; los demás negocios, inscritos o no, pueden publicar su registro sin clave.

## 2. Cómo publicar un registro ABIZ

### Campos obligatorios

| Campo | Qué poner | Ejemplo |
| --- | --- | --- |
| `record_version` | Siempre `abiz1` | `abiz1` |
| `business_name` | El nombre público del negocio | `Chocolates Mitad del Mundo S.A.` |
| `country` | El código de país ISO 3166-1 alfa-2, en minúsculas | `ec` |
| `identity_host` | El host, con ruta opcional, donde se sirve el registro; debe coincidir con `h` en el DNS | `chocolatesmitaddelmundo.ec.to.co` |
| `domains` | Los dominios que usted controla y que el registro reclama | `["chocolatesmitad.example"]` |

### La clave de empresa opcional `k`

`k` es opcional para cualquier negocio. Si la publica, debe seguir la sección 4.2 de la especificación y ser igual al `business_key` del registro. Las claves se comparan sin distinguir mayúsculas de minúsculas, pero la forma canónica lleva el código de país en minúsculas y el número de registro en mayúsculas.

Formato: `ec-` seguido del número de expediente que la Superintendencia de Compañías, Valores y Seguros asigna a cada compañía. La sección 4.2.2 de la especificación no menciona Ecuador, así que la clave no lleva código de subdivisión, y debe usarse el número del registro nacional de sociedades, no el RUC: la especificación solo admite un número fiscal donde lo nombra expresamente, como México y Brasil. El formato que se muestra es ilustrativo: no hemos podido confirmar el formato exacto del número. Use el número tal como figura en su inscripción. Si después de la normalización contiene caracteres que no sean letras y cifras ASCII, o si no identifica a la empresa de forma única en todo el país, omita `k`. Los negocios que no son compañías bajo control de la Superintendencia (por ejemplo, personas naturales inscritas solo en un registro mercantil cantonal) deben omitir `k`.

**Normalización del número (sección 4.2.3).** Parta del número tal como lo emite el registro. Aplique la normalización Unicode NFKC; quite espacios, guiones, puntos y barras; pase las letras a mayúsculas; conserve los ceros a la izquierda y los prefijos de letras. Si queda cualquier otro carácter, como paréntesis, `&`, `Ñ` o una letra acentuada, el número no puede expresarse y no puede publicar una clave de empresa: omita `k`, `business_key` y `registration_number`.

**Ejemplo (ficticio):** el expediente `123456` da la clave `ec-123456`.

Si incluye `business_key` y `registration_number` en el registro, incluya los dos, y haga que la parte numérica de la clave coincida con `registration_number`. Incluirlos no le obliga a publicar `k` en el DNS. Si publica `k`, el registro debe contener el `business_key` correspondiente.

### El registro DNS TXT

Publique un único registro TXT que empiece por `v=abiz1` en `_abiz.` seguido de su dominio. Use la forma compacta, sin espacios (sección 3.1.1), y un TTL de 300 segundos:

```dns
_abiz.chocolatesmitad.example. 300 IN TXT "v=abiz1;k=ec-123456;h=chocolatesmitaddelmundo.ec.to.co;p=PJr3o2ISeqSFZ1RpGSIxlQxPDZSdtddvx+OCZsHbeQE="
```

Un negocio sin número de registro, o que prefiera no publicarlo, simplemente omite `k`:

```dns
_abiz.puestodelmercado.example. 300 IN TXT "v=abiz1;h=puestodelmercado.biz.to.co;p=Dkn2mKhPZR98t3sl+tHQqv6p9shjRW8sJQVuFaKMSek="
```

### Ejemplo de registro (JSON)

Este ejemplo es ficticio. Supera el validador de referencia.

```json
{
  "record_version": "abiz1",
  "business_name": "Chocolates Mitad del Mundo S.A.",
  "country": {
    "code": "EC",
    "name": "Ecuador"
  },
  "business_key": "ec-123456",
  "registration_number": "123456",
  "identity_host": "chocolatesmitaddelmundo.ec.to.co",
  "domains": [
    "chocolatesmitad.example"
  ],
  "public_key": "PJr3o2ISeqSFZ1RpGSIxlQxPDZSdtddvx+OCZsHbeQE=",
  "description": "Chocolate de cacao fino de aroma.",
  "website": "https://chocolatesmitad.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Quito",
        "country": {
          "code": "EC"
        }
      },
      "opening_hours": {
        "time_zone": "America/Guayaquil",
        "weekly": [
          {
            "day": "monday",
            "periods": [
              {
                "opens": "09:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "tuesday",
            "periods": [
              {
                "opens": "09:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "wednesday",
            "periods": [
              {
                "opens": "09:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "thursday",
            "periods": [
              {
                "opens": "09:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "friday",
            "periods": [
              {
                "opens": "09:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "saturday",
            "periods": []
          },
          {
            "day": "sunday",
            "periods": []
          }
        ]
      },
      "public": true
    }
  ],
  "signature": "7VGUtPlfhcJ5QxNL0tBciL8Uu9GCmjzP/nC/Q4HBzLUAibSMPVJhwEOdGMsxI/AIkajRuZKX7R6N+DinIK5SCw=="
}
```

### Dónde se aloja el registro

Puede servir el registro usted mismo desde cualquier URL HTTPS que devuelva el documento JSON, por ejemplo `h=www.chocolatesmitad.example`, o usar cualquier proveedor compatible. ABIZ no exige un proveedor ni un esquema de nombres concreto. Elija lo que elija, el `identity_host` del registro debe coincidir con `h`, y `domains` debe incluir el dominio donde publica el registro TXT.

Antes de publicar, compruebe el registro y el valor DNS con el validador de referencia:

```sh
python scripts/validate.py record.json \
  --domain chocolatesmitad.example \
  --dns-value 'v=abiz1;k=ec-123456;h=chocolatesmitaddelmundo.ec.to.co;p=PJr3o2ISeqSFZ1RpGSIxlQxPDZSdtddvx+OCZsHbeQE='
```

## 3. Proveedores y MCP

El Model Context Protocol (MCP) es un protocolo abierto que permite a los asistentes de IA usar herramientas y leer datos de servicios externos de forma estándar. Un registro ABIZ puede incluir un `mcp_server_url` opcional: la dirección HTTPS de un servidor MCP que responda preguntas sobre el negocio, como horarios, servicios o disponibilidad. ABIZ no exige un servidor MCP, y que figure en el registro no lo avala: el software compatible no debe llamarlo automáticamente solo porque aparezca en un registro, y debe aplicar sus propios controles de acceso.

Por ejemplo, un proveedor puede alojar el registro de Chocolates Mitad del Mundo en `chocolatesmitaddelmundo.ec.to.co`, publicar el registro DNS TXT mediante su propio proceso de configuración e indicar su servidor MCP en `mcp_server_url`. Puede cambiar de proveedor, o pasar a alojarlo usted mismo, cambiando `h` y el `identity_host` del registro.

## 4. Claves y firmas (ABIZ 1.1)

- **`p` es obligatoria.** `v` y `h` son obligatorios; `k` es opcional. `p` debe ser una clave pública Ed25519: 32 bytes en bruto, base64 estándar, exactamente 44 caracteres, un único `=` final. Base64url no se acepta (sección 3.3.2). Cualquier otro valor, como una cadena hexadecimal, invalida toda la aserción.
- **Ejemplo** (la clave es un ejemplo desechable; su clave privada se ha descartado). No la copie nunca: publique su propia clave. Una aserción ABIZ 1.1 debe incluir `p`.

  ```dns
  _abiz.chocolatesmitad.example. 300 IN TXT "v=abiz1;k=ec-123456;h=chocolatesmitaddelmundo.ec.to.co;p=PJr3o2ISeqSFZ1RpGSIxlQxPDZSdtddvx+OCZsHbeQE="
  ```

- **La clave privada pertenece al negocio.** Nunca debe aparecer en el DNS, en el registro ni en un repositorio público. Un proveedor puede generarla y custodiarla por usted (modo alojado), pero debe permitirle exportarla en cualquier momento, por ejemplo en formato PKCS#8, y borrar su copia si se lo pide (sección 3.3.4).
- **Firmas.** El software puede comprobar una firma Ed25519 separada con la clave publicada. La firma del registro cubre la forma canónica RFC 8785 del registro sin el miembro `signature`, y se comprueba con `public_key`, que debe ser igual a `p` (SPEC sección 4.6). Una firma sobre otro mensaje solo tiene sentido si ambas partes lo han acordado.
- **Rotación y revocación.** Genere un nuevo par Ed25519, publique la nueva clave pública en la aserción DNS o well-known, vuelva a firmar el registro con la nueva clave privada y haga que `public_key` sea ese mismo `p`. Tenga en cuenta la caché y la propagación del DNS; la clave anterior deja de ser la vigente cuando vence el TTL. Quitar solo `p` no es una revocación válida mientras la aserción ABIZ 1.1 siga publicada: para retirarla, elimine la declaración DNS o well-known completa. ABIZ 1.1 no publica claves retiradas (se rechaza una propiedad `retired_keys`).
- **Qué demuestra una clave.** Muestra qué clave publicó quien controla el dominio. No firma por sí misma el registro TXT ni demuestra la identidad legal. Use DNSSEC si su proveedor de DNS lo admite.

## 5. Qué verán las herramientas de IA

El software compatible que lea su registro puede responder preguntas como:

- «¿Chocolates Mitad del Mundo abre el sábado?»
- «¿Qué servicios ofrece Chocolates Mitad del Mundo en Quito?»
- «¿Cuál es el sitio web oficial de Chocolates Mitad del Mundo?»
- «¿Chocolates Mitad del Mundo tiene número de registro publicado?»

También puede indicar que el dominio y el registro se refieren el uno al otro, que el registro cumple el esquema y si hay publicada una clave `p` válida.

**Límites.** Un registro ABIZ no es prueba de inscripción legal. Una herramienta solo puede describir una empresa como confirmada en el registro oficial si lo ha comprobado por separado y lo indica así. ABIZ no es un aval, ni un sello de calidad, ni una promesa de visibilidad en ningún servicio de IA.

## 6. Notas prácticas locales

**Número de registro.** El número de expediente aparece en el portal de la [Superintendencia de Compañías, Valores y Seguros](https://www.supercias.gob.ec/). El RUC figura en el certificado del [Servicio de Rentas Internas](https://www.sri.gob.ec/), pero no se usa en `k`.

**Cómo añadir el registro TXT.** Entre donde se gestiona el DNS de su dominio: normalmente el registrador donde lo compró o su proveedor de alojamiento. Añada un registro de tipo TXT con el nombre `_abiz` (algunos paneles piden el nombre completo, `_abiz.chocolatesmitad.example`), pegue el valor sin las comillas y, si el panel lo permite, ponga un TTL de 300 segundos. Los dominios `.ec` se registran en [NIC.EC](https://www.nic.ec).

**Privacidad.** El registro y el valor TXT son públicos. Publique solo los datos que quiera hacer públicos. Una persona que trabaja por cuenta propia no debería publicar su domicilio ni su teléfono personal; es mejor omitir un campo que marcarlo como privado (sección 4.3). En Ecuador rige la Ley Orgánica de Protección de Datos Personales.

## 7. Más información

- [Especificación ABIZ](../../../SPEC.md) (en inglés): sección 3.1.1 (sintaxis TXT), sección 3.3 (claves `p`), sección 4.2 (claves de empresa)
- [JSON Schema del registro](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Validador de referencia](../../../scripts/validate.py) y [ejemplos](../../../examples/)
- [Todas las guías de América del Sur](index.md)
