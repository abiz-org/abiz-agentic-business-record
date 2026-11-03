# Convertirse en una empresa agéntica con ABIZ en Guinea Ecuatorial

*Guía para ABIZ 1.1 (propuesta). La [especificación (SPEC.md, en inglés)](../../../SPEC.md) es el texto de referencia: si esta guía y la especificación difieren, prevalece la especificación.* El español es la lengua principal de la administración; el francés y el portugués también son oficiales.

## 1. Qué significa para una empresa en Guinea Ecuatorial

A los asistentes de IA se les pregunta cada vez más «¿cuál es la web real de esta empresa?» o «¿quién gestiona este comercio?». ABIZ (Agentic Business Record) es una norma abierta que permite a una empresa de Guinea Ecuatorial publicar una sola vez sus datos públicos en un formato que esas herramientas pueden leer: un breve registro DNS TXT en un dominio que la empresa controla, que apunta a una ficha de empresa en JSON servida por HTTPS. Como ese puntero está en el DNS de la propia empresa, una herramienta puede comprobar que la ficha la publicó quien controla el dominio, en lugar de fiarse de un directorio no oficial o de una suposición.

## 2. Cómo publicar un registro ABIZ

### Campos obligatorios

Toda ficha de empresa lleva estos cinco campos (sección 4.1 de la SPEC):

| Campo | Ejemplo y regla |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | el nombre público que conocen los clientes, por ejemplo `Carpintería Bioko` |
| `country` | `gq`, el código ISO 3166-1 alfa-2, en minúsculas |
| `identity_host` | `carpinteriabioko.gq.to.co`, que debe coincidir exactamente con `h` en el DNS |
| `domains` | `["carpinteriabioko.example"]`, que debe incluir el dominio que lleva `_abiz` |

### Clave de empresa opcional `k`

`k` es opcional para cualquier empresa, inscrita o no. Si la publica, debe ser igual al campo `business_key` de la ficha, que entonces también debe contener `registration_number`. Para Guinea Ecuatorial, la forma es:

```text
gq-<registration-number>
```

Guinea Ecuatorial no usa subdivisión: no añada códigos de provincia, región ni ciudad. La sección 4.2.2 de la SPEC solo exige subdivisión para Estados Unidos, las sociedades provinciales de Canadá y los Emiratos Árabes Unidos, y la prohíbe en el resto de países.

**Qué número:** el número RCCM (Registro de Comercio y de Crédito Mobiliario, sistema de la OHADA) tal como figura en el certificado de inscripción, con sus letras. Como incluye el código del país y del registro, lo tratamos como único a nivel nacional. Es nuestra interpretación de la sección 4.2.2 de la SPEC, que no menciona la OHADA; conviene confirmarla. Por ejemplo `GQ/MAL/2023/B/123` para Malabo.

**Normalización (sección 4.2.3 de la SPEC):** parta del número tal como lo expide el registro, aplique la normalización Unicode NFKC, elimine espacios, `-`, `.`, `/` y guiones, y pase las letras a mayúsculas. Conserve los ceros iniciales y los prefijos de letras. El resultado solo puede contener letras y dígitos ASCII; si no es así, no se puede publicar una clave de empresa: omita `k`, `business_key` y `registration_number`.

**Ejemplo (ficticio):** `GQ/MAL/2023/B/123` pasa a ser `GQMAL2023B123`, así que `k=gq-GQMAL2023B123`. En la ficha: `"business_key": "gq-GQMAL2023B123"` y `"registration_number": "GQMAL2023B123"`. Las claves se comparan sin distinguir mayúsculas; la forma canónica lleva el código de país en minúsculas y el número en mayúsculas.

**Compruébelo:** no hemos podido confirmar el formato exacto de este número en una fuente oficial, por lo que el ejemplo es solo orientativo. Use el número tal como figura en su documento oficial de inscripción. Si no está claro qué número identifica a la empresa a nivel nacional, no publique `k` hasta estar seguro.

**Empresarios individuales:** si el único número que tiene es personal, como un documento nacional de identidad o un número fiscal personal, no publique `k`. Omita `k`, `business_key` y `registration_number`; el registro sigue siendo válido.

### Registro DNS TXT

Publique un único registro TXT en `_abiz` bajo su dominio, en forma compacta, sin espacios y con `v=abiz1` en primer lugar:

```dns
_abiz.carpinteriabioko.example. 300 IN TXT "v=abiz1;k=gq-GQMAL2023B123;h=carpinteriabioko.gq.to.co;p=h7+5j5IoZHQl6ayOcSYb1BySREBCD8toiUKR4b5yO3E="
```

El valor `p` anterior es una clave de ejemplo desechable, generada para esta página. No la copie nunca: publique su propia clave. Una aserción ABIZ 1.1 debe incluir `p`. Todos los nombres, números y dominios de esta página son ficticios.

Sin las etiquetas opcionales `k` y `p`, esto también es válido:

```dns
_abiz.carpinteriabioko.example. 300 IN TXT "v=abiz1;h=carpinteriabioko.gq.to.co;p=h7+5j5IoZHQl6ayOcSYb1BySREBCD8toiUKR4b5yO3E="
```

El registro de la empresa servido como `application/json` en `https://carpinteriabioko.gq.to.co`:

```json
{
  "record_version": "abiz1",
  "business_name": "Carpintería Bioko",
  "country": "gq",
  "business_key": "gq-GQMAL2023B123",
  "registration_number": "GQMAL2023B123",
  "identity_host": "carpinteriabioko.gq.to.co",
  "domains": [
    "carpinteriabioko.example"
  ],
  "public_key": "h7+5j5IoZHQl6ayOcSYb1BySREBCD8toiUKR4b5yO3E=",
  "signature": "ClqvogD2sf2vP9r7LM3gViz72DDK+6N/mbdvoRRmtlaRC/aThP0TiE2A/rsJWouz0gMQvFbspBe/IEJe1GK3BQ=="
}
```

Para comprobar una ficha antes de publicarla, ejecute el validador de referencia desde una copia de este repositorio:

```sh
python scripts/validate.py record.json --domain carpinteriabioko.example --dns-value 'v=abiz1;k=gq-GQMAL2023B123;h=carpinteriabioko.gq.to.co;p=h7+5j5IoZHQl6ayOcSYb1BySREBCD8toiUKR4b5yO3E='
```

Puede alojar la ficha JSON usted mismo, en cualquier servidor HTTPS, o usar cualquier proveedor compatible. ABIZ no exige un proveedor concreto.

## 3. Usar un proveedor y MCP

El Model Context Protocol (MCP) es un protocolo abierto que permite a los asistentes de IA llamar a herramientas y leer datos de servidores externos de forma estándar. Una ficha puede incluir el campo opcional `mcp_server_url`, la dirección HTTPS de un servidor MCP de la empresa, por ejemplo para reservas o información de productos. ABIZ no avala ese servidor: las herramientas deben aplicar sus propios controles de acceso (sección 4.2.6 de la SPEC).

Un proveedor puede alojar la ficha y publicar el puntero DNS por usted. Por ejemplo, una sociedad inscrita en Guinea Ecuatorial con la ficha alojada en to.co podría usar el host `carpinteriabioko.gq.to.co`, lo que da el valor DNS `v=abiz1;k=gq-GQMAL2023B123;h=carpinteriabioko.gq.to.co;p=h7+5j5IoZHQl6ayOcSYb1BySREBCD8toiUKR4b5yO3E=`. Una empresa no inscrita podría usar un host basado en su localidad, como `carpinteriabioko-malabo.biz.to.co`. Cualquier proveedor compatible, o su propio servidor, funciona igual.

## 4. Claves y firmas (ABIZ 1.1)

ABIZ 1.1 añade una clave de firma opcional. La etiqueta DNS `p` puede contener una clave pública Ed25519: 44 caracteres en base64 estándar que terminan en un único `=` (sección 3.3.2 de la SPEC). La empresa, o un proveedor que actúe en su nombre, guarda la clave privada correspondiente y puede firmar contenidos que otros verifican con la clave publicada. La clave privada pertenece siempre a la empresa, y un proveedor de alojamiento debe permitirle exportarla.

- `v` y `h` son obligatorios. `p` es obligatoria. `k` es opcional. `p` debe ser una clave válida de 32 bytes en base64 estándar, 44 caracteres, un único `=` final. Base64url no se acepta. Cualquier otro valor, como un antiguo token hexadecimal de ABIZ 1.0, invalida toda la aserción.
- Solo se publica la clave vigente. Para cambiarla, genere un nuevo par Ed25519, publique la nueva clave pública, vuelva a firmar la ficha y haga que `public_key` sea ese mismo `p`. Tenga en cuenta la caché del DNS. Quitar solo `p` no es una revocación válida mientras la aserción ABIZ 1.1 siga publicada: para retirarla, elimine la declaración completa. En ABIZ 1.1 las claves retiradas no se publican, ni en el DNS ni en la ficha.
- Una clave muestra quién controla el DNS del dominio. No prueba la identidad jurídica.

## 5. Qué verán las herramientas de IA

Una herramienta compatible que lea su ficha puede responder a preguntas como:

1. ¿Cuál es la web oficial de Carpintería Bioko?
2. ¿Qué dominios pertenecen a esta empresa?
3. ¿Qué número de inscripción indica la empresa, y en qué país?
4. ¿Qué ofrece y cuándo abre?

**Límites:** ABIZ muestra lo que ha publicado el titular de un dominio. No prueba que la empresa esté legalmente inscrita, que su número sea auténtico ni que un servicio de IA, una administración o un proveedor la respalde. Cuando sea importante, herramientas y personas deben consultar el registro oficial.

## 6. Notas prácticas locales

- **Registro:** Registro Mercantil y RCCM (OHADA). No indicamos una web porque no hemos podido confirmar una dirección oficial que funcione.
- **Añadir el registro TXT:** en la configuración DNS de su registrador o proveedor de DNS, añada un registro TXT con el nombre `_abiz` (algunos paneles piden el nombre completo, `_abiz.sudominio.gq`), el valor indicado y un TTL de 300 segundos. Los dominios `.gq` funcionan igual que `.com` o cualquier otro. Mantenga el valor entero siempre que pueda y no divida nunca `p`.
- **Protección de datos:** Compruebe las normas de protección de datos aplicables en Guinea Ecuatorial antes de publicar datos personales. Una ficha ABIZ es pública. Publique solo información empresarial que acepte compartir y omita domicilios particulares y teléfonos privados (sección 4.3 de la SPEC).

## 7. Más información

- [Especificación ABIZ (SPEC.md, en inglés)](../../../SPEC.md)
- [Esquema JSON de la ficha de empresa](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Validador de referencia](../../../scripts/validate.py)
- [Guías ABIZ por país: África](index.md)
