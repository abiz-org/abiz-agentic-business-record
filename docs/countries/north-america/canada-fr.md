# Devenir une entreprise agentique avec ABIZ au Canada

*Guide de la spécification publiée ABIZ 1.1. [SPEC.md](../../../SPEC.md) est le texte de référence : en cas d’écart entre ce guide et la spécification, c’est la spécification qui s’applique.* Ce guide est rédigé en français du Québec. Une [version anglaise](canada-en.md) est aussi offerte.

## 1. Ce que cela signifie pour une entreprise au Canada

De plus en plus de gens posent à des assistants d’IA des questions comme « quelle boulangerie près de chez moi est ouverte dimanche? » ou « ce site appartient-il vraiment à cette entreprise? ». ABIZ (Agentic Business Record) est une norme ouverte qui permet à une entreprise de publier ses renseignements publics sous une forme que les logiciels compatibles peuvent trouver et vérifier : un petit document JSON contenant ces renseignements, et un enregistrement DNS TXT, sur le domaine de l’entreprise, qui pointe vers ce document.

Grâce à ABIZ, un assistant compatible peut partir de votre domaine, trouver votre fiche, la valider à l’aide du JSON Schema publié et confirmer que le domaine et la fiche renvoient l’un à l’autre. Cela vaut pour les sociétés immatriculées comme pour les entreprises qui ne le sont pas. ABIZ ne garantit pas qu’un assistant vous trouvera, vous classera ou vous recommandera, et ce n’est pas un label officiel.

Au Canada, une société par actions peut ajouter son numéro d’entreprise ou de société comme clé d’entreprise; une entreprise individuelle ou une société de personnes peut publier sa fiche sans clé.

## 2. Publier une fiche ABIZ

### Champs obligatoires

| Champ | Contenu | Exemple |
| --- | --- | --- |
| `record_version` | Toujours `abiz1` | `abiz1` |
| `business_name` | Le nom public de l’entreprise | `Boulangerie du Vieux-Port inc.` |
| `country` | Le code de pays ISO 3166-1 alpha-2, en minuscules | `ca` |
| `identity_host` | L’hôte, avec un chemin facultatif, où la fiche est servie; il doit correspondre à `h` dans le DNS | `boulangerieduvieuxport.qc.ca.to.co` |
| `domains` | Les domaines que vous contrôlez et que la fiche revendique | `["boulangerieduvieuxport.example"]` |

### La clé d’entreprise facultative `k`

`k` est facultative pour toutes les entreprises. Si vous la publiez, elle doit respecter la section 4.2 de la spécification et être identique au `business_key` de la fiche. La casse ne compte pas dans la comparaison des clés, mais la forme canonique met le code de pays en minuscules et le numéro d’immatriculation en majuscules.

Au Canada, la forme de la clé dépend du lieu de constitution (section 4.2.2) :

- **Société provinciale ou territoriale :** `ca-<province>-<numéro>`, avec le code à deux lettres de la province ou du territoire de constitution et le numéro de son registre. Au Québec, on utilise le numéro d’entreprise du Québec (NEQ), à 10 chiffres : `ca-qc-1234567890`. En Ontario, le numéro de société de l’Ontario donne `ca-on-` suivi de ce numéro; en Colombie-Britannique, le préfixe `BC` est conservé, par exemple `ca-bc-BC1234567`.
- **Société fédérale** (Loi canadienne sur les sociétés par actions) : `ca-<numéro>`, **sans** province, avec le numéro de société de Corporations Canada, chiffre de contrôle compris. `1234567-8` devient `ca-12345678`.
- **Seul le lieu de constitution compte.** L’immatriculation d’une société dans une autre province (comme société extraprovinciale) ne change pas la clé.
- **Pas le numéro d’entreprise de l’ARC.** Le numéro d’entreprise (NE) de l’Agence du revenu du Canada est un numéro fiscal; ne l’utilisez pas dans `k`.
- **Entreprises individuelles et sociétés de personnes.** La spécification ne précise pas quel numéro utiliser dans ces cas. D’ici là, omettez `k`.

**Normaliser le numéro (section 4.2.3).** Partez du numéro tel que le registre le délivre. Appliquez la normalisation Unicode NFKC; supprimez les espaces, traits d’union, points et barres obliques; mettez les lettres en majuscules; conservez les zéros initiaux et les préfixes en lettres. S’il reste un autre caractère, par exemple des parenthèses, `&` ou une lettre accentuée, le numéro ne peut pas être exprimé et vous ne pouvez pas publier de clé : omettez `k`, `business_key` et `registration_number`.

**Exemple (fictif) :** le NEQ `1234567890` donne la clé `ca-qc-1234567890`.

Si vous ajoutez `business_key` et `registration_number` à la fiche, ajoutez les deux, et la partie numérique de la clé doit être égale à `registration_number`. Les inclure ne vous oblige pas à publier `k` dans le DNS. Si vous publiez `k`, la fiche doit contenir le `business_key` correspondant.

### L’enregistrement DNS TXT

Publiez un seul enregistrement TXT commençant par `v=abiz1` à `_abiz.` suivi de votre domaine. Utilisez la forme compacte, sans espaces (section 3.1.1), avec un TTL de 300 secondes :

```dns
_abiz.boulangerieduvieuxport.example. 300 IN TXT "v=abiz1;k=ca-qc-1234567890;h=boulangerieduvieuxport.qc.ca.to.co;p=yqBQ0dRFxFPK8ivZR02YUAp6Rhq60QT7V5TtYHz17jM="
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
  "business_name": "Boulangerie du Vieux-Port inc.",
  "country": "ca",
  "business_key": "ca-qc-1234567890",
  "registration_number": "1234567890",
  "identity_host": "boulangerieduvieuxport.qc.ca.to.co",
  "domains": [
    "boulangerieduvieuxport.example"
  ],
  "public_key": "yqBQ0dRFxFPK8ivZR02YUAp6Rhq60QT7V5TtYHz17jM=",
  "description": "Boulangerie artisanale et viennoiseries dans le Vieux-Port.",
  "website": "https://boulangerieduvieuxport.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Québec",
        "region": {
          "code": "CA-QC",
          "name": "Québec"
        },
        "country": {
          "code": "CA"
        }
      },
      "opening_hours": {
        "time_zone": "America/Toronto",
        "weekly": [
          {
            "day": "monday",
            "periods": []
          },
          {
            "day": "tuesday",
            "periods": [
              {
                "opens": "07:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "wednesday",
            "periods": [
              {
                "opens": "07:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "thursday",
            "periods": [
              {
                "opens": "07:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "friday",
            "periods": [
              {
                "opens": "07:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "saturday",
            "periods": [
              {
                "opens": "07:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "sunday",
            "periods": [
              {
                "opens": "07:00",
                "closes": "18:00"
              }
            ]
          }
        ]
      },
      "public": true
    }
  ],
  "signature": "VJ2vK0jiVqA71QuwK+rY+RHDWRmAeI9H6zkIqHvxa42Z6XgWQVEnvWKInXdCanIUfJ2AxZNtyn9r7+iGGnHTDQ=="
}
```

### Où héberger la fiche

Vous pouvez servir la fiche vous-même depuis n’importe quelle URL HTTPS qui renvoie le document JSON, par exemple `h=www.boulangerieduvieuxport.example/abiz.json`, ou faire appel à n’importe quel fournisseur compatible. ABIZ n’impose ni fournisseur ni schéma de nommage. Dans tous les cas, l’`identity_host` de la fiche doit correspondre à `h`, et `domains` doit inclure le domaine où vous publiez l’enregistrement TXT.

Avant de publier, vérifiez la fiche et la valeur DNS avec le validateur de référence :

```sh
python scripts/validate.py record.json \
  --domain boulangerieduvieuxport.example \
  --dns-value 'v=abiz1;k=ca-qc-1234567890;h=boulangerieduvieuxport.qc.ca.to.co;p=yqBQ0dRFxFPK8ivZR02YUAp6Rhq60QT7V5TtYHz17jM='
```

## 3. Fournisseurs et MCP

Le Model Context Protocol (MCP) est un protocole ouvert qui permet aux assistants d’IA d’utiliser des outils et de lire des données provenant de services externes de façon standardisée. Une fiche ABIZ peut contenir un champ facultatif `mcp_server_url` : l’adresse HTTPS d’un serveur MCP capable de répondre à des questions sur l’entreprise, comme les heures d’ouverture, les services ou les disponibilités. ABIZ n’exige pas de serveur MCP, et sa mention dans une fiche ne le cautionne pas : un logiciel compatible ne doit pas l’appeler automatiquement du seul fait qu’il figure dans une fiche, et doit appliquer ses propres contrôles d’accès.

Par exemple, un fournisseur peut héberger la fiche de la Boulangerie du Vieux-Port à `boulangerieduvieuxport.qc.ca.to.co`, publier l’enregistrement DNS TXT au moyen de sa propre procédure de configuration et indiquer son serveur MCP dans `mcp_server_url`. Vous pouvez changer de fournisseur, ou héberger la fiche vous-même, en modifiant `h` et l’`identity_host` de la fiche.

## 4. Clés et signatures (ABIZ 1.1)

- **`p` est obligatoire.** `v` et `h` sont obligatoires ; `k` est facultative. `p` doit être une clé publique Ed25519 : 32 octets bruts, en base64 standard, exactement 44 caractères, un seul `=` final. Le base64url n’est pas accepté (section 3.3.2). Toute autre valeur, comme un ancien jeton hexadécimal d’ABIZ 1.0, rend toute l’assertion invalide.
- **Exemple** (clé d’exemple jetable; sa clé privée a été détruite). Ne la copiez jamais : publiez votre propre clé. Une assertion ABIZ 1.1 doit inclure `p`.

  ```dns
  _abiz.boulangerieduvieuxport.example. 300 IN TXT "v=abiz1;k=ca-qc-1234567890;h=boulangerieduvieuxport.qc.ca.to.co;p=yqBQ0dRFxFPK8ivZR02YUAp6Rhq60QT7V5TtYHz17jM="
  ```

- **La clé privée appartient à l’entreprise.** Elle ne doit jamais figurer dans le DNS, dans la fiche ni dans un dépôt public. Un fournisseur peut la générer et la conserver pour vous (mode hébergé), mais il doit vous permettre de l’exporter à tout moment, par exemple au format PKCS#8, et supprimer sa copie à votre demande (section 3.3.4).
- **Signatures.** Un logiciel peut vérifier une signature Ed25519 détachée à l’aide de la clé publiée. La signature de la fiche couvre la forme canonique RFC 8785 de la fiche sans le membre `signature`, et se vérifie avec `public_key`, qui doit être égal à `p` (SPEC section 4.6). Une signature sur un autre message n’a de sens que si les deux parties ont convenu de ce message.
- **Rotation et clés retirées.** Pour changer de clé, publiez la nouvelle dans `p`; l’ancienne cesse d’être la clé courante une fois le TTL de l’enregistrement TXT écoulé. ABIZ 1.1 ne publie pas les clés retirées : ni dans le DNS, ni dans la fiche (une propriété `retired_keys` est rejetée).
- **Ce que prouve une clé.** Elle indique quelle clé la personne qui contrôle le domaine a publiée. Elle ne signe pas à elle seule l’enregistrement TXT et ne prouve pas l’identité juridique. Utilisez DNSSEC si votre hébergeur DNS le permet.

## 5. Ce que verront les outils d’IA

Un logiciel compatible qui lit votre fiche peut répondre à des questions comme :

- « La Boulangerie du Vieux-Port est-elle ouverte le dimanche? »
- « Que vend la Boulangerie du Vieux-Port à Québec? »
- « Quel est le site officiel de la Boulangerie du Vieux-Port? »
- « La Boulangerie du Vieux-Port a-t-elle publié son NEQ? »

Il peut aussi indiquer que le domaine et la fiche renvoient l’un à l’autre, que la fiche respecte le schéma et si une clé `p` valide est publiée.

**Limites.** Une fiche ABIZ ne prouve pas l’immatriculation légale. Un outil ne peut présenter une entreprise comme confirmée par le registre officiel que s’il a vérifié ce registre séparément et le signale comme tel. ABIZ n’est ni une caution, ni un gage de qualité, ni une promesse de visibilité dans un service d’IA.

## 6. Notes pratiques locales

**Numéro d’immatriculation.** Le NEQ figure sur les documents du [Registraire des entreprises du Québec](https://www.quebec.ca/entreprises-et-travailleurs-autonomes/registraire-des-entreprises). Ailleurs au pays : le [Registre des entreprises de l’Ontario](https://www.ontario.ca/fr/page/registre-des-entreprises-de-lontario), [BC Registries](https://www.bcregistry.gov.bc.ca/) et, pour les sociétés fédérales, [Corporations Canada](https://ised-isde.canada.ca/site/corporations-canada/fr).

**Ajouter l’enregistrement TXT.** Connectez-vous là où le DNS de votre domaine est géré : en général chez le registraire où vous avez acheté le domaine, ou chez votre hébergeur. Ajoutez un enregistrement de type TXT nommé `_abiz` (certains panneaux demandent le nom complet, `_abiz.boulangerieduvieuxport.example`), collez la valeur sans les guillemets et, si possible, fixez le TTL à 300 secondes. Les noms de domaine `.ca` relèvent de l’[ACEI (CIRA)](https://www.cira.ca/) et se vendent par l’intermédiaire de registraires accrédités.

**Vie privée.** La fiche et la valeur TXT sont publiques. Ne publiez que des renseignements destinés à l’être. Un travailleur autonome ne devrait pas publier son adresse personnelle ni son numéro de téléphone personnel; mieux vaut omettre un champ que de le marquer comme privé (section 4.3). Au Québec, la Loi sur la protection des renseignements personnels dans le secteur privé, modernisée par la Loi 25, s’applique aux entreprises. Ailleurs, la LPRPDE fédérale s’applique, sous la surveillance du [Commissariat à la protection de la vie privée du Canada](https://www.priv.gc.ca/fr/); l’Alberta et la Colombie-Britannique ont leurs propres lois.

## 7. Pour aller plus loin

- [Spécification ABIZ](../../../SPEC.md) (en anglais) : section 3.1.1 (syntaxe TXT), section 3.3 (clés `p`), section 4.2 (clés d’entreprise)
- [JSON Schema de la fiche](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Validateur de référence](../../../scripts/validate.py) et [exemples](../../../examples/)
- [Tous les guides d’Amérique du Nord](index.md)
