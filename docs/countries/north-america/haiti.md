# Devenir une entreprise agentique avec ABIZ en Haïti

*Guide d’ABIZ 1.1 (proposée). [SPEC.md](../../../SPEC.md) est le texte de référence : en cas d’écart entre ce guide et la spécification, c’est la spécification qui s’applique.* Haïti a deux langues officielles, le français et le créole haïtien (kreyòl); ce guide est en français, la langue des formalités d’entreprise.

## 1. Ce que cela signifie pour une entreprise en Haïti

De plus en plus de gens posent à des assistants d’IA des questions comme « quelle boulangerie près de chez moi est ouverte dimanche? » ou « ce site appartient-il vraiment à cette entreprise? ». ABIZ (Agentic Business Record) est une norme ouverte qui permet à une entreprise de publier ses renseignements publics sous une forme que les logiciels compatibles peuvent trouver et vérifier : un petit document JSON contenant ces renseignements, et un enregistrement DNS TXT, sur le domaine de l’entreprise, qui pointe vers ce document.

Grâce à ABIZ, un assistant compatible peut partir de votre domaine, trouver votre fiche, la valider à l’aide du JSON Schema publié et confirmer que le domaine et la fiche renvoient l’un à l’autre. Cela vaut pour les sociétés immatriculées comme pour les entreprises qui ne le sont pas. ABIZ ne garantit pas qu’un assistant vous trouvera, vous classera ou vous recommandera, et ce n’est pas un label officiel.

En Haïti, une société immatriculée au ministère du Commerce et de l’Industrie peut ajouter son numéro d’immatriculation comme clé d’entreprise; une entreprise non immatriculée peut publier sa fiche sans clé.

## 2. Publier une fiche ABIZ

### Champs obligatoires

| Champ | Contenu | Exemple |
| --- | --- | --- |
| `record_version` | Toujours `abiz1` | `abiz1` |
| `business_name` | Le nom public de l’entreprise | `Boulangerie Soleil S.A.` |
| `country` | Le code de pays ISO 3166-1 alpha-2, en minuscules | `ht` |
| `identity_host` | L’hôte, avec un chemin facultatif, où la fiche est servie; il doit correspondre à `h` dans le DNS | `boulangeriesoleil.ht.to.co` |
| `domains` | Les domaines que vous contrôlez et que la fiche revendique | `["boulangeriesoleil.example"]` |

### La clé d’entreprise facultative `k`

`k` est facultative pour toutes les entreprises. Si vous la publiez, elle doit respecter la section 4.2 de la spécification et être identique au `business_key` de la fiche. La casse ne compte pas dans la comparaison des clés, mais la forme canonique met le code de pays en minuscules et le numéro d’immatriculation en majuscules.

Forme : `ht-` suivi du numéro d’immatriculation de la société au registre du ministère du Commerce et de l’Industrie (MCI), qui est national. La section 4.2.2 de la spécification ne mentionne pas Haïti; la clé n’a donc pas de code de subdivision. N’utilisez pas le NIF : la spécification n’admet un numéro fiscal que là où elle le nomme expressément, comme au Mexique et au Brésil. Le format présenté ici est illustratif : nous n’avons pas pu confirmer le format exact du numéro. Utilisez le numéro tel qu’il figure sur vos documents. Si, après normalisation, il contient autre chose que des lettres et des chiffres ASCII, ou s’il n’identifie pas la société de façon unique dans tout le pays, omettez `k`.

**Normaliser le numéro (section 4.2.3).** Partez du numéro tel que le registre le délivre. Appliquez la normalisation Unicode NFKC; supprimez les espaces, traits d’union, points et barres obliques; mettez les lettres en majuscules; conservez les zéros initiaux et les préfixes en lettres. S’il reste un autre caractère, par exemple des parenthèses, `&` ou une lettre accentuée, le numéro ne peut pas être exprimé et vous ne pouvez pas publier de clé : omettez `k`, `business_key` et `registration_number`.

**Exemple (fictif) :** le numéro d’immatriculation `12345` donne la clé `ht-12345`.

Si vous ajoutez `business_key` et `registration_number` à la fiche, ajoutez les deux, et la partie numérique de la clé doit être égale à `registration_number`. Les inclure ne vous oblige pas à publier `k` dans le DNS. Si vous publiez `k`, la fiche doit contenir le `business_key` correspondant.

### L’enregistrement DNS TXT

Publiez un seul enregistrement TXT commençant par `v=abiz1` à `_abiz.` suivi de votre domaine. Utilisez la forme compacte, sans espaces (section 3.1.1), avec un TTL de 300 secondes :

```dns
_abiz.boulangeriesoleil.example. 300 IN TXT "v=abiz1;k=ht-12345;h=boulangeriesoleil.ht.to.co;p=e3ffdmvEqh32AcAHhbQjyZ8EthXuwHP8Nxh14VbMfr0="
```

Une entreprise sans numéro d’immatriculation, ou qui préfère ne pas le publier, omet simplement `k` :

```dns
_abiz.etaldumarche.example. 300 IN TXT "v=abiz1;h=etaldumarche.biz.to.co"
```

### Exemple de fiche (JSON)

Cet exemple est fictif. Il passe le validateur de référence.

```json
{
  "record_version": "abiz1",
  "business_name": "Boulangerie Soleil S.A.",
  "country": "ht",
  "business_key": "ht-12345",
  "registration_number": "12345",
  "identity_host": "boulangeriesoleil.ht.to.co",
  "domains": [
    "boulangeriesoleil.example"
  ],
  "public_key": "e3ffdmvEqh32AcAHhbQjyZ8EthXuwHP8Nxh14VbMfr0=",
  "description": "Pain, pâtés et pain patate.",
  "website": "https://boulangeriesoleil.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Port-au-Prince",
        "country": {
          "code": "HT"
        }
      },
      "opening_hours": {
        "time_zone": "America/Port-au-Prince",
        "weekly": [
          {
            "day": "monday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "tuesday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "wednesday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "thursday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "friday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "saturday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "18:00"
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
  "signature": "EkfItcQaoWdfchPq/qYd+6SwC/POKBzZPbDGhQ1mKjb05T+4nzEaz2EZnlRuzyGF+vKMAJcsZ5viPL4ol9UCCA=="
}
```

### Où héberger la fiche

Vous pouvez servir la fiche vous-même depuis n’importe quelle URL HTTPS qui renvoie le document JSON, par exemple `h=www.boulangeriesoleil.example/abiz.json`, ou faire appel à n’importe quel fournisseur compatible. ABIZ n’impose ni fournisseur ni schéma de nommage. Dans tous les cas, l’`identity_host` de la fiche doit correspondre à `h`, et `domains` doit inclure le domaine où vous publiez l’enregistrement TXT.

Avant de publier, vérifiez la fiche et la valeur DNS avec le validateur de référence :

```sh
python scripts/validate.py record.json \
  --domain boulangeriesoleil.example \
  --dns-value 'v=abiz1;k=ht-12345;h=boulangeriesoleil.ht.to.co;p=e3ffdmvEqh32AcAHhbQjyZ8EthXuwHP8Nxh14VbMfr0='
```

## 3. Fournisseurs et MCP

Le Model Context Protocol (MCP) est un protocole ouvert qui permet aux assistants d’IA d’utiliser des outils et de lire des données provenant de services externes de façon standardisée. Une fiche ABIZ peut contenir un champ facultatif `mcp_server_url` : l’adresse HTTPS d’un serveur MCP capable de répondre à des questions sur l’entreprise, comme les heures d’ouverture, les services ou les disponibilités. ABIZ n’exige pas de serveur MCP, et sa mention dans une fiche ne le cautionne pas : un logiciel compatible ne doit pas l’appeler automatiquement du seul fait qu’il figure dans une fiche, et doit appliquer ses propres contrôles d’accès.

Par exemple, un fournisseur peut héberger la fiche de la Boulangerie Soleil à `boulangeriesoleil.ht.to.co`, publier l’enregistrement DNS TXT au moyen de sa propre procédure de configuration et indiquer son serveur MCP dans `mcp_server_url`. Vous pouvez changer de fournisseur, ou héberger la fiche vous-même, en modifiant `h` et l’`identity_host` de la fiche.

## 4. Clés et signatures (ABIZ 1.1)

- **`p` est obligatoire.** `v` et `h` sont obligatoires ; `k` est facultative. `p` doit être une clé publique Ed25519 : 32 octets bruts, en base64 standard, exactement 44 caractères, un seul `=` final. Le base64url n’est pas accepté (section 3.3.2). Toute autre valeur, comme un ancien jeton hexadécimal d’ABIZ 1.0, rend toute l’assertion invalide.
- **Exemple** (clé d’exemple jetable; sa clé privée a été détruite). Ne la copiez jamais : publiez votre propre clé. Une assertion ABIZ 1.1 doit inclure `p`.

  ```dns
  _abiz.boulangeriesoleil.example. 300 IN TXT "v=abiz1;k=ht-12345;h=boulangeriesoleil.ht.to.co;p=e3ffdmvEqh32AcAHhbQjyZ8EthXuwHP8Nxh14VbMfr0="
  ```

- **La clé privée appartient à l’entreprise.** Elle ne doit jamais figurer dans le DNS, dans la fiche ni dans un dépôt public. Un fournisseur peut la générer et la conserver pour vous (mode hébergé), mais il doit vous permettre de l’exporter à tout moment, par exemple au format PKCS#8, et supprimer sa copie à votre demande (section 3.3.4).
- **Signatures.** Un logiciel peut vérifier une signature Ed25519 détachée à l’aide de la clé publiée. La signature de la fiche couvre la forme canonique RFC 8785 de la fiche sans le membre `signature`, et se vérifie avec `public_key`, qui doit être égal à `p` (SPEC section 4.6). Une signature sur un autre message n’a de sens que si les deux parties ont convenu de ce message.
- **Rotation et clés retirées.** Pour changer de clé, publiez la nouvelle dans `p`; l’ancienne cesse d’être la clé courante une fois le TTL de l’enregistrement TXT écoulé. ABIZ 1.1 ne publie pas les clés retirées : ni dans le DNS, ni dans la fiche (une propriété `retired_keys` est rejetée).
- **Ce que prouve une clé.** Elle indique quelle clé la personne qui contrôle le domaine a publiée. Elle ne signe pas à elle seule l’enregistrement TXT et ne prouve pas l’identité juridique. Utilisez DNSSEC si votre hébergeur DNS le permet.

## 5. Ce que verront les outils d’IA

Un logiciel compatible qui lit votre fiche peut répondre à des questions comme :

- « La Boulangerie Soleil est-elle ouverte le dimanche? »
- « Que vend la Boulangerie Soleil à Port-au-Prince? »
- « Quel est le site officiel de la Boulangerie Soleil? »
- « La Boulangerie Soleil a-t-elle publié un numéro d’immatriculation? »

Il peut aussi indiquer que le domaine et la fiche renvoient l’un à l’autre, que la fiche respecte le schéma et si une clé `p` valide est publiée.

**Limites.** Une fiche ABIZ ne prouve pas l’immatriculation légale. Un outil ne peut présenter une entreprise comme confirmée par le registre officiel que s’il a vérifié ce registre séparément et le signale comme tel. ABIZ n’est ni une caution, ni un gage de qualité, ni une promesse de visibilité dans un service d’IA.

## 6. Notes pratiques locales

**Numéro d’immatriculation.** Les sociétés sont immatriculées auprès du [ministère du Commerce et de l’Industrie](https://www.mci.gouv.ht/).

**Ajouter l’enregistrement TXT.** Connectez-vous là où le DNS de votre domaine est géré : en général chez le registraire où vous avez acheté le domaine, ou chez votre hébergeur. Ajoutez un enregistrement de type TXT nommé `_abiz` (certains panneaux demandent le nom complet, `_abiz.boulangeriesoleil.example`), collez la valeur sans les guillemets et, si possible, fixez le TTL à 300 secondes.

**Vie privée.** La fiche et la valeur TXT sont publiques. Ne publiez que des renseignements destinés à l’être. Un travailleur autonome ne devrait pas publier son adresse personnelle ni son numéro de téléphone personnel; mieux vaut omettre un champ que de le marquer comme privé (section 4.3). Vérifiez les règles en vigueur sur les données personnelles avant de publier des renseignements sur des personnes.

## 7. Pour aller plus loin

- [Spécification ABIZ](../../../SPEC.md) (en anglais) : section 3.1.1 (syntaxe TXT), section 3.3 (clés `p`), section 4.2 (clés d’entreprise)
- [JSON Schema de la fiche](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Validateur de référence](../../../scripts/validate.py) et [exemples](../../../examples/)
- [Tous les guides d’Amérique du Nord](index.md)
