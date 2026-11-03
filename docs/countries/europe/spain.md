# Convertirse en una empresa agéntica con ABIZ en España

*Guía de ABIZ 1.1 (propuesta). El texto de referencia es la [especificación (SPEC.md, en inglés)](../../../SPEC.md): si esta guía y la especificación difieren, prevalece la especificación.*

## 1. Qué significa para una empresa en España

Cada vez más personas preguntan a los asistentes de IA por las empresas: quiénes son, qué ofrecen, dónde encontrarlas. Con ABIZ (Agentic Business Record), una empresa publica una ficha pública y legible por máquinas con sus propios datos, como nombre, país, web, servicios y horario, y en su propio dominio un registro DNS que apunta a esa ficha.

Solo la empresa, o quien actúe en su nombre, puede modificar el DNS de su dominio. Por eso, un software compatible puede encontrar la ficha a partir del dominio y comprobar que el dominio y la ficha se remiten mutuamente, en lugar de reunir datos de páginas web dispersas. ABIZ es abierto e independiente de proveedores: no exige afiliación, cuotas ni un proveedor concreto.

## 2. Cómo publicar una ficha ABIZ

### Campos obligatorios

La ficha de la empresa es un documento JSON que debe cumplir el [esquema normativo](../../../schemas/abiz-business-record-v1.schema.json). Hay cinco campos obligatorios:

| Campo | Ejemplo | Notas |
| --- | --- | --- |
| `record-version` | `abiz1` | Siempre este valor |
| `business-name` | `Panadería García S.L.` | El nombre público, normalmente como figura en el registro, con la forma jurídica si la usa |
| `country` | `es` | Código de país ISO 3166-1 alfa-2; la forma canónica es en minúsculas |
| `identity-host` | `panaderiagarcia.es.to.co` | Exactamente el valor DNS `h`: un nombre de host con ruta opcional, sin `https://` |
| `domains` | `["panaderiagarcia.example"]` | Los dominios que reclama la ficha, incluido el que lleva `_abiz` |

### Clave de empresa `k` (opcional)

`k` es opcional para cualquier empresa, esté inscrita o no. Si la publica, la ficha debe incluir también `business-key` y `registration-number`, y `k` debe coincidir con `business-key`.

En España la clave es `es-` seguido del número, sin subdivisión territorial: una clave con una parte intermedia, como `es-xx-…`, no es válida.

- **Registro:** El Registro Mercantil es provincial (Registro Mercantil de Madrid, de Valencia…), por lo que sus datos de inscripción (tomo, folio, hoja) no sirven como clave nacional. Se usa el NIF, identificador nacional y único que asigna la [Agencia Tributaria](https://sede.agenciatributaria.gob.es/) y que figura en el [Registro Mercantil Central](https://www.rmc.es/)
- **Número que se usa:** el NIF de la sociedad: una letra, siete cifras y un carácter de control (antes llamado CIF)
- **Cómo escribirlo:** parta del número tal como se emite, aplique la normalización Unicode NFKC, elimine espacios, `-`, `.`, `/` y otros guiones y escriba las letras en mayúsculas. Los ceros iniciales y los prefijos de letras se conservan. El resultado solo puede contener letras y cifras ASCII.

Ejemplo (número inventado): `B-12345678` se convierte en `B12345678`. La ficha contiene entonces `"registration-number": "B12345678"` y `"business-key": "es-B12345678"`, y el DNS lleva `k=es-B12345678`. Conserve la letra inicial. No use el prefijo `ES` del NIF-IVA.

Las claves se comparan sin distinguir mayúsculas y minúsculas, pero publique la forma canónica: código de país en minúsculas y número en mayúsculas.

### Registro DNS TXT

Publique un único registro TXT de ABIZ en `_abiz` de su dominio, en forma compacta y sin espacios:

```dns
_abiz.panaderiagarcia.example. 300 IN TXT "v=abiz1;k=es-B12345678;h=panaderiagarcia.es.to.co;p=KtIkewzCLg7RKtfdv8V5nsK0xg2eFCL/Zam/Y8FKfdM="
```

- `v=abiz1` debe ir primero. `h` es obligatorio; `k` y `p` son opcionales.
- Los nombres de las etiquetas van en minúsculas y distinguen mayúsculas y minúsculas. Ninguna etiqueta puede repetirse.
- Se recomienda un TTL de 300 segundos.

El valor `p` anterior es una clave de ejemplo desechable. No la copie nunca: publique su propia clave u omita `p`.

### Ficha de la empresa (JSON)

La ficha que se sirve en `https://panaderiagarcia.es.to.co` como `application/json`:

```json
{
  "record-version": "abiz1",
  "business-name": "Panadería García S.L.",
  "country": "es",
  "business-key": "es-B12345678",
  "registration-number": "B12345678",
  "identity-host": "panaderiagarcia.es.to.co",
  "domains": [
    "panaderiagarcia.example"
  ],
  "description": "Panadería artesana en Valencia.",
  "website": "https://panaderiagarcia.example",
  "locations": [
    {
      "kind": "trading",
      "city": "Valencia",
      "country": "es",
      "public": true
    }
  ]
}
```

Con el validador de referencia puede comprobar en local la ficha y el valor DNS:

```sh
python scripts/validate.py record.json --domain panaderiagarcia.example --dns-value 'v=abiz1;k=es-B12345678;h=panaderiagarcia.es.to.co;p=KtIkewzCLg7RKtfdv8V5nsK0xg2eFCL/Zam/Y8FKfdM='
```

### Por su cuenta o con un proveedor

Puede servir la ficha usted mismo en cualquier host HTTPS que controle o usar cualquier proveedor compatible. ABIZ no impone proveedor ni esquema de nombres de host. En todo caso, la ficha debe servirse por HTTPS y usted debe controlar el dominio que lleva `_abiz`.

## 3. Proveedores y MCP

MCP (Model Context Protocol) es un protocolo abierto con el que los asistentes de IA llaman a herramientas y leen datos de servidores externos. Un proveedor puede gestionar un servidor MCP para que un asistente obtenga directamente su ficha pública. Puede indicarlo en el campo opcional `mcp-server-url`. ABIZ no exige un servidor MCP, y una herramienta no debería llamarlo automáticamente solo porque figure en una ficha.

Por ejemplo, un proveedor puede publicar su ficha en `panaderiagarcia.es.to.co` y gestionar un servidor MCP. Un asistente conectado a ese servidor puede preguntar por el horario o los servicios de Panadería García S.L. y recibir los datos de su ficha, en lugar de adivinarlos. to.co, uno de esos proveedores, explica ABIZ en una [página en español](https://to.co/es-es/abiz).

## 4. Claves y firmas (ABIZ 1.1)

ABIZ 1.1 permite publicar una clave pública Ed25519 en la etiqueta DNS `p`. `p` es opcional. Si aparece, debe ser la codificación base64 estándar de la clave de 32 bytes: 44 caracteres que terminan en un único `=`, en una sola cadena DNS. Cualquier otro valor, como un token hexadecimal de ABIZ 1.0 o una clave en base64url, invalida todo el registro.

La clave privada correspondiente pertenece a la empresa y nunca se publica. Si un proveedor la custodia por usted, debe permitirle exportarla. Un software puede comprobar una firma hecha con la clave privada usando la clave publicada en el DNS. ABIZ 1.1 todavía no define qué bytes cubre una firma de la ficha.

Para cambiar de clave, publique una nueva en `p`; para revocarla, elimine `p`. En ABIZ 1.1 las claves retiradas no se publican, ni en el DNS ni en la ficha. La clave muestra qué clave publicó quien controla el dominio; no acredita la identidad jurídica.

## 5. Qué ven las herramientas de IA

Con una ficha válida, un asistente compatible puede responder preguntas como:

- «¿Es Panadería García S.L. una empresa de Valencia?»
- «¿Qué ofrece Panadería García S.L. y cuál es su horario?»
- «¿Es panaderiagarcia.example la web oficial de Panadería García S.L.?»
- «¿Qué número de identificación declara Panadería García S.L.?»

Los límites importan. ABIZ muestra que un dominio y una ficha se remiten mutuamente. No prueba que la empresa esté inscrita legalmente, que un número sea auténtico ni que alguien la avale. Una herramienta que no haya consultado por sí misma el Registro Mercantil no debe presentar la empresa como verificada. ABIZ no garantiza que ningún servicio de IA encuentre, clasifique o recomiende una empresa.

## 6. Notas prácticas

### Dónde encontrar el número

El NIF figura en la tarjeta de identificación fiscal, en las facturas y en el aviso legal de su web. Los datos registrales se consultan en el [Registro Mercantil Central](https://www.rmc.es/) y en [registradores.org](https://www.registradores.org/). El NIF de un autónomo es su DNI o NIE personal: en ese caso no publique la clave, porque identifica a una persona.

### Añadir el registro TXT

Añada el registro donde se gestione el DNS de su dominio, normalmente en su registrador o proveedor de alojamiento. El registro de los dominios `.es` es [dominios.es](https://www.dominios.es/), pero el registro TXT se añade en su registrador o proveedor DNS; sirve cualquiera que admita registros TXT. Cree un registro de tipo TXT con el nombre `_abiz` (algunos paneles piden el nombre completo, `_abiz.panaderiagarcia.example`), el valor exactamente como arriba y un TTL de 300. No añada espacios dentro del valor y elimine cualquier registro ABIZ anterior para que solo quede uno.

### Privacidad y publicación de datos

El RGPD se aplica a los datos personales de la ficha, por ejemplo el nombre de un autónomo o de una persona de contacto. El [Comité Europeo de Protección de Datos](https://www.edpb.europa.eu/) enlaza con cada autoridad nacional; en España es la Agencia Española de Protección de Datos. Todo lo que contiene una ficha ABIZ es público: publique solo datos que quiera hacer públicos. Un autónomo no debería publicar su domicilio particular: la especificación exige omitir las direcciones privadas, no marcarlas como privadas. Una dirección genérica como `info@` es mejor que un correo personal.

## 7. Más información

- [Especificación ABIZ (SPEC.md, en inglés)](../../../SPEC.md): sintaxis DNS (sección 3.1.1), clave `p` (sección 3.3), claves de empresa (sección 4.2)
- [Esquema JSON normativo](../../../schemas/abiz-business-record-v1.schema.json)
- [Validador de referencia, scripts/validate.py](../../../scripts/validate.py)
- [Todas las guías de Europa](index.md)
