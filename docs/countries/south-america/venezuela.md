# Convertirse en un negocio agéntico con ABIZ en Venezuela

*Guía de ABIZ 1.1 (propuesta). [SPEC.md](../../../SPEC.md) es el texto de referencia: si esta guía y la especificación difieren, prevalece la especificación.*

## 1. Qué significa para una empresa en Venezuela

Cada vez más personas preguntan a los asistentes de IA cosas como «¿qué panadería cerca de mí abre el domingo?» o «¿este sitio web es de verdad de esta empresa?». ABIZ (Agentic Business Record) es un estándar abierto que permite a un negocio publicar sus datos públicos de forma que el software compatible pueda encontrarlos y comprobarlos: un pequeño documento JSON con esos datos y un registro DNS TXT en el dominio propio del negocio que apunta a él.

Con ABIZ, un asistente compatible puede partir de su dominio, encontrar su registro, validarlo con el JSON Schema publicado y confirmar que el dominio y el registro se refieren el uno al otro. Sirve tanto para empresas inscritas como para negocios sin inscripción. No garantiza que ningún asistente le encuentre, le posicione o le recomiende, y no es un sello oficial.

En Venezuela, cualquier negocio, inscrito o no, puede publicar un registro ABIZ. La clave de empresa opcional `k` todavía no está disponible para Venezuela (véase más abajo). Esta guía no presupone ningún proveedor: los ejemplos alojan el registro en el propio dominio del negocio.

## 2. Cómo publicar un registro ABIZ

### Campos obligatorios

| Campo | Qué poner | Ejemplo |
| --- | --- | --- |
| `record_version` | Siempre `abiz1` | `abiz1` |
| `business_name` | El nombre público del negocio | `Panadería La Candelaria, C.A.` |
| `country` | El código de país ISO 3166-1 alfa-2, en minúsculas | `ve` |
| `identity_host` | El host, con ruta opcional, donde se sirve el registro; debe coincidir con `h` en el DNS | `www.panaderialacandelaria.example/abiz.json` |
| `domains` | Los dominios que usted controla y que el registro reclama | `["panaderialacandelaria.example"]` |

### La clave de empresa opcional `k`

`k` es opcional para cualquier negocio. Si la publica, debe seguir la sección 4.2 de la especificación y ser igual al `business_key` del registro. Las claves se comparan sin distinguir mayúsculas de minúsculas, pero la forma canónica lleva el código de país en minúsculas y el número de registro en mayúsculas.

**Por ahora, no hay clave de empresa para Venezuela.** Según la sección 4.2.2 de la especificación, fuera de los países que nombra, `k` debe ser el número del registro nacional de empresas. En Venezuela, las sociedades se inscriben en el registro mercantil de su circunscripción, y sus datos de inscripción no son únicos en todo el país. La especificación dice que un país cuyos registros son solo locales o regionales y que no figura en su primera tabla todavía no puede llevar una clave de empresa. Por eso, omita `k`, `business_key` y `registration_number` hasta que una revisión de la especificación lo resuelva. El RIF no sirve como clave: la especificación solo admite un número fiscal en los países donde lo nombra expresamente, como México (RFC) y Brasil (CNPJ). Todo lo demás de esta guía funciona igual sin `k`.

**Normalización del número (sección 4.2.3).** Parta del número tal como lo emite el registro. Aplique la normalización Unicode NFKC; quite espacios, guiones, puntos y barras; pase las letras a mayúsculas; conserve los ceros a la izquierda y los prefijos de letras. Si queda cualquier otro carácter, como paréntesis, `&`, `Ñ` o una letra acentuada, el número no puede expresarse y no puede publicar una clave de empresa: omita `k`, `business_key` y `registration_number`.

Si incluye `business_key` y `registration_number` en el registro, incluya los dos, y haga que la parte numérica de la clave coincida con `registration_number`. Incluirlos no le obliga a publicar `k` en el DNS. Si publica `k`, el registro debe contener el `business_key` correspondiente.

### El registro DNS TXT

Publique un único registro TXT que empiece por `v=abiz1` en `_abiz.` seguido de su dominio. Use la forma compacta, sin espacios (sección 3.1.1), y un TTL de 300 segundos:

```dns
_abiz.panaderialacandelaria.example. 300 IN TXT "v=abiz1;h=www.panaderialacandelaria.example/abiz.json;p=v8Ggu5ha9uyzh1NTF+AJS+GDSRBxJLRTzfElFl/h8TM="
```

### Ejemplo de registro (JSON)

Este ejemplo es ficticio. Supera el validador de referencia.

```json
{
  "record_version": "abiz1",
  "business_name": "Panadería La Candelaria, C.A.",
  "country": "ve",
  "identity_host": "www.panaderialacandelaria.example/abiz.json",
  "domains": [
    "panaderialacandelaria.example"
  ],
  "public_key": "v8Ggu5ha9uyzh1NTF+AJS+GDSRBxJLRTzfElFl/h8TM=",
  "description": "Panadería y pastelería en La Candelaria.",
  "website": "https://panaderialacandelaria.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Caracas",
        "country": {
          "code": "VE"
        }
      },
      "opening_hours": {
        "time_zone": "America/Caracas",
        "weekly": [
          {
            "day": "monday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "19:00"
              }
            ]
          },
          {
            "day": "tuesday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "19:00"
              }
            ]
          },
          {
            "day": "wednesday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "19:00"
              }
            ]
          },
          {
            "day": "thursday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "19:00"
              }
            ]
          },
          {
            "day": "friday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "19:00"
              }
            ]
          },
          {
            "day": "saturday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "19:00"
              }
            ]
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
  "signature": "3rM6ZFthCd0JshY40rZBm1QkZqAzQop5SE2Gz+E3k5xFn2aRRuJzvyb5BQ6VFzL/1WJSR+3mSyGbH4RRKEx0Ag=="
}
```

### Dónde se aloja el registro

Puede servir el registro usted mismo desde cualquier URL HTTPS que devuelva el documento JSON, por ejemplo `h=www.panaderialacandelaria.example/abiz.json`, o usar cualquier proveedor compatible. ABIZ no exige un proveedor ni un esquema de nombres concreto. Elija lo que elija, el `identity_host` del registro debe coincidir con `h`, y `domains` debe incluir el dominio donde publica el registro TXT.

Antes de publicar, compruebe el registro y el valor DNS con el validador de referencia:

```sh
python scripts/validate.py record.json \
  --domain panaderialacandelaria.example \
  --dns-value 'v=abiz1;h=www.panaderialacandelaria.example/abiz.json;p=v8Ggu5ha9uyzh1NTF+AJS+GDSRBxJLRTzfElFl/h8TM='
```

## 3. Proveedores y MCP

El Model Context Protocol (MCP) es un protocolo abierto que permite a los asistentes de IA usar herramientas y leer datos de servicios externos de forma estándar. Un registro ABIZ puede incluir un `mcp_server_url` opcional: la dirección HTTPS de un servidor MCP que responda preguntas sobre el negocio, como horarios, servicios o disponibilidad. ABIZ no exige un servidor MCP, y que figure en el registro no lo avala: el software compatible no debe llamarlo automáticamente solo porque aparezca en un registro, y debe aplicar sus propios controles de acceso.

Por ejemplo, un proveedor puede alojar el registro en `www.panaderialacandelaria.example/abiz.json` e indicar su servidor MCP en `mcp_server_url`. Puede cambiar de proveedor, o pasar a alojarlo usted mismo, cambiando `h` y el `identity_host` del registro.

## 4. Claves y firmas (ABIZ 1.1)

- **`p` es opcional.** Si está presente, debe ser una clave pública Ed25519 en base64 estándar: exactamente 44 caracteres, terminada en un único `=`, que se decodifica en 32 bytes (sección 3.3.2). Cualquier otro valor, como un antiguo token hexadecimal de ABIZ 1.0 o una clave en base64url, invalida toda la aserción. Sustitúyalo por una clave o elimínelo.
- **Ejemplo** (la clave es un ejemplo desechable; su clave privada se ha descartado). No la copie nunca: publique su propia clave u omita `p`.

  ```dns
  _abiz.panaderialacandelaria.example. 300 IN TXT "v=abiz1;h=www.panaderialacandelaria.example/abiz.json;p=v8Ggu5ha9uyzh1NTF+AJS+GDSRBxJLRTzfElFl/h8TM="
  ```

- **La clave privada pertenece al negocio.** Nunca debe aparecer en el DNS, en el registro ni en un repositorio público. Un proveedor puede generarla y custodiarla por usted (modo alojado), pero debe permitirle exportarla en cualquier momento, por ejemplo en formato PKCS#8, y borrar su copia si se lo pide (sección 3.3.4).
- **Firmas.** El software puede comprobar una firma Ed25519 separada con la clave publicada. ABIZ 1.1 todavía no define qué bytes de un registro cubre una firma, así que una comprobación de firma solo tiene sentido para un mensaje que ambas partes hayan acordado.
- **Rotación y claves retiradas.** Para rotar, publique la nueva clave en `p`; la anterior deja de ser la vigente cuando vence el TTL del registro TXT. ABIZ 1.1 no publica claves retiradas: ni en el DNS ni en el registro (se rechaza una propiedad `retired_keys`).
- **Qué demuestra una clave.** Muestra qué clave publicó quien controla el dominio. No firma por sí misma el registro TXT ni demuestra la identidad legal. Use DNSSEC si su proveedor de DNS lo admite.

## 5. Qué verán las herramientas de IA

El software compatible que lea su registro puede responder preguntas como:

- «¿Panadería La Candelaria abre el sábado?»
- «¿Qué servicios ofrece Panadería La Candelaria en Caracas?»
- «¿Cuál es el sitio web oficial de Panadería La Candelaria?»

También puede indicar que el dominio y el registro se refieren el uno al otro, que el registro cumple el esquema y si hay publicada una clave `p` válida.

**Límites.** Un registro ABIZ no es prueba de inscripción legal. Una herramienta solo puede describir una empresa como confirmada en el registro oficial si lo ha comprobado por separado y lo indica así. ABIZ no es un aval, ni un sello de calidad, ni una promesa de visibilidad en ningún servicio de IA.

## 6. Notas prácticas locales

**Número de registro.** El RIF figura en el comprobante emitido por el SENIAT. La inscripción mercantil corresponde a los registros mercantiles adscritos al [SAREN](https://www.saren.gob.ve/).

**Cómo añadir el registro TXT.** Entre donde se gestiona el DNS de su dominio: normalmente el registrador donde lo compró o su proveedor de alojamiento. Añada un registro de tipo TXT con el nombre `_abiz` (algunos paneles piden el nombre completo, `_abiz.panaderialacandelaria.example`), pegue el valor sin las comillas y, si el panel lo permite, ponga un TTL de 300 segundos. Los dominios `.ve` se registran en [NIC.VE](https://www.nic.ve/). Algunos proveedores internacionales de dominios y DNS no ofrecen servicio en Venezuela; elija uno que pueda prestarlo legalmente.

**Privacidad.** El registro y el valor TXT son públicos. Publique solo los datos que quiera hacer públicos. Una persona que trabaja por cuenta propia no debería publicar su domicilio ni su teléfono personal; es mejor omitir un campo que marcarlo como privado (sección 4.3). Compruebe la normativa vigente sobre protección de datos personales antes de publicar datos de personas.

## 7. Más información

- [Especificación ABIZ](../../../SPEC.md) (en inglés): sección 3.1.1 (sintaxis TXT), sección 3.3 (claves `p`), sección 4.2 (claves de empresa)
- [JSON Schema del registro](../../../schemas/abiz-business-record-v1.schema.json)
- [Validador de referencia](../../../scripts/validate.py) y [ejemplos](../../../examples/)
- [Todas las guías de América del Sur](index.md)
