# Devenir une entreprise agentique avec ABIZ à Monaco

*Guide pour la spécification publiée ABIZ 1.1. Le texte de référence est la [spécification (SPEC.md, en anglais)](../../../SPEC.md) : en cas de divergence entre ce guide et la spécification, la spécification prévaut.*

## 1. Ce que cela signifie pour une entreprise à Monaco

On interroge de plus en plus les assistants d'IA sur les entreprises : qui elles sont, ce qu'elles proposent, où les trouver. ABIZ (Agentic Business Record) permet à une entreprise de publier une fiche publique, lisible par les machines, avec ses propres informations (nom, pays, site web, services, horaires) et, sur son propre domaine, un enregistrement DNS qui pointe vers cette fiche.

Seule l'entreprise, ou une personne qu'elle mandate, peut modifier le DNS de son domaine. Un logiciel compatible peut donc trouver la fiche à partir du domaine et vérifier que le domaine et la fiche renvoient l'un à l'autre, au lieu de reconstituer les informations à partir de pages web éparses. ABIZ est ouvert et indépendant de tout fournisseur : aucune adhésion, aucun frais ni aucun fournisseur particulier n'est requis.

## 2. Publier une fiche ABIZ

### Champs obligatoires

La fiche d'entreprise est un document JSON qui doit être conforme au [schéma normatif](../../../schemas/abiz-business-record-v1.1.schema.json). Cinq champs sont obligatoires :

| Champ | Exemple | Remarques |
| --- | --- | --- |
| `record_version` | `abiz1` | Toujours cette valeur |
| `business_name` | `Riviera Yachting SARL` | Le nom public, en général tel qu'il figure au registre, avec la forme juridique si vous l'utilisez |
| `country` | `mc` | Code pays ISO 3166-1 alpha-2 ; la forme canonique est en minuscules |
| `identity_host` | `rivierayachting.mc.to.co` | Exactement la valeur DNS `h` : un nom d'hôte avec un chemin facultatif, sans `https://` |
| `domains` | `["rivierayachting.example"]` | Les domaines revendiqués par la fiche, y compris celui qui porte `_abiz` |

### Clé d'entreprise `k` (facultative)

`k` est facultatif pour toute entreprise, immatriculée ou non. Si vous le publiez, la fiche doit aussi contenir `business_key` et `registration_number`, et `k` doit être égal à `business_key`.

À Monaco, la clé s'écrit `mc-` suivi du numéro d'immatriculation, sans subdivision : une clé comportant une partie intermédiaire, comme `mc-xx-…`, est invalide.

- **Registre :** Répertoire du Commerce et de l'Industrie (RCI), tenu par la [Direction du Développement Économique](https://www.rci.gouv.mc/)
- **Numéro à utiliser :** le numéro RCI, par exemple `12 S 12345` (année, lettre de catégorie, numéro d'ordre)
- **Écriture :** partez du numéro tel que le registre l'attribue, appliquez la normalisation Unicode NFKC, supprimez les espaces, `-`, `.`, `/` et les autres tirets, puis mettez les lettres en majuscules. Les zéros initiaux et les préfixes en lettres sont conservés. Le résultat ne doit contenir que des lettres et des chiffres ASCII.

Exemple (numéro fictif) : `12 S 12345` devient `12S12345`. La fiche contient alors `"registration_number": "12S12345"` et `"business_key": "mc-12S12345"`, et le DNS porte `k=mc-12S12345`. Conservez la lettre de catégorie.

Les clés se comparent sans tenir compte de la casse, mais publiez la forme canonique : code pays en minuscules, numéro en majuscules.

### Enregistrement DNS TXT

Publiez un seul enregistrement TXT ABIZ sous `_abiz` sur votre domaine, sous forme compacte, sans espaces :

```dns
_abiz.rivierayachting.example. 300 IN TXT "v=abiz1;k=mc-12S12345;h=rivierayachting.mc.to.co;p=ALvkwEs8/MU73gYkmjN9N6MUQAVMZiV1JuIU3kLoMfg="
```

- `v=abiz1` doit venir en premier. `h` et `p` sont obligatoires ; `k` est facultatif.
- Les noms de balises sont en minuscules et sensibles à la casse. Une balise ne doit pas apparaître deux fois.
- Une durée de vie (TTL) de 300 secondes est recommandée.

La valeur `p` ci-dessus est une clé d'exemple jetable. Ne la copiez jamais : publiez votre propre clé. Une assertion ABIZ 1.1 doit inclure `p`.

### Fiche d'entreprise (JSON)

La fiche servie à l'adresse `https://rivierayachting.mc.to.co`, au format `application/json` :

```json
{
  "record_version": "abiz1",
  "business_name": "Riviera Yachting SARL",
  "country": "mc",
  "business_key": "mc-12S12345",
  "registration_number": "12S12345",
  "identity_host": "rivierayachting.mc.to.co",
  "domains": [
    "rivierayachting.example"
  ],
  "public_key": "ALvkwEs8/MU73gYkmjN9N6MUQAVMZiV1JuIU3kLoMfg=",
  "description": "Services nautiques à Monaco.",
  "website": "https://rivierayachting.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Monaco",
        "country": {
          "code": "MC"
        }
      },
      "public": true
    }
  ],
  "signature": "wjYRrbI8rzFxg8xKo0r+mqt0wKOGwXa1qCzJJPWcPYK886F4i9D1cqiyOabsiNHz1GFlIraxgeils191x2WpBQ=="
}
```

Le validateur de référence vérifie localement la fiche et la valeur DNS :

```sh
python scripts/validate.py record.json --domain rivierayachting.example --dns-value 'v=abiz1;k=mc-12S12345;h=rivierayachting.mc.to.co;p=ALvkwEs8/MU73gYkmjN9N6MUQAVMZiV1JuIU3kLoMfg='
```

### Hébergement par vous-même ou par un fournisseur

Vous pouvez servir la fiche vous-même sur tout hôte HTTPS que vous contrôlez, ou passer par n'importe quel fournisseur compatible. ABIZ n'impose ni fournisseur ni schéma de nom d'hôte. Dans tous les cas, la fiche doit être servie en HTTPS et vous devez contrôler le domaine qui porte `_abiz`.

## 3. Fournisseurs et MCP

MCP (Model Context Protocol) est un protocole ouvert qui permet aux assistants d'IA d'appeler des outils et de lire des données sur des serveurs externes. Un fournisseur peut exploiter un serveur MCP grâce auquel un assistant obtient directement votre fiche publique. Vous pouvez l'indiquer dans le champ facultatif `mcp_server_url`. ABIZ n'exige pas de serveur MCP, et un outil ne doit pas en appeler un automatiquement au seul motif qu'il figure dans une fiche.

Par exemple, un fournisseur peut servir votre fiche à l'adresse `rivierayachting.mc.to.co` et exploiter un serveur MCP. Un assistant connecté à ce serveur peut alors demander les horaires ou les services de Riviera Yachting SARL et obtenir les informations de votre fiche, au lieu de les deviner.

## 4. Clés et signatures (ABIZ 1.1)

ABIZ 1.1 exige une clé publique Ed25519 dans la balise DNS `p`. `v` et `h` sont obligatoires. `p` est obligatoire. `k` est facultatif. `p` doit être 32 octets bruts en base64 standard : 44 caractères terminés par un seul `=`, dans une seule chaîne DNS. Le base64url n'est pas accepté. Toute autre valeur, comme un jeton hexadécimal ABIZ 1.0, rend l'ensemble de l'enregistrement invalide.

La clé privée correspondante appartient à l'entreprise et n'est jamais publiée. Un fournisseur qui la conserve pour vous doit vous permettre de l'exporter. Un logiciel peut vérifier une signature produite avec la clé privée à l'aide de la clé publiée dans le DNS. La signature de la fiche couvre la forme canonique RFC 8785 de la fiche sans le membre `signature`, et se vérifie avec `public_key`, qui doit être égal à `p` (SPEC section 4.6).

Pour changer de clé, générez une nouvelle paire Ed25519, publiez la nouvelle clé publique dans l'assertion DNS ou well-known, resignez la fiche avec la nouvelle clé privée, et faites correspondre `public_key` à ce `p`. Tenez compte du cache DNS. Supprimer seulement `p` n'est pas une révocation valable tant que l'assertion ABIZ 1.1 reste en place : pour la retirer, supprimez toute la déclaration. Les clés retirées ne sont pas publiées en ABIZ 1.1, ni dans le DNS ni dans la fiche. La clé montre quelle clé le titulaire du domaine a publiée ; elle ne prouve pas l'identité juridique.

## 5. Ce que voient les outils d'IA

Avec une fiche valide, un assistant compatible peut répondre à des questions comme :

- « Riviera Yachting SARL est-elle une entreprise située à Monaco ? »
- « Que propose Riviera Yachting SARL, et quels sont ses horaires ? »
- « rivierayachting.example est-il le site officiel de Riviera Yachting SARL ? »
- « Quel numéro d'immatriculation Riviera Yachting SARL indique-t-elle pour elle-même ? »

Les limites comptent. ABIZ montre qu'un domaine et une fiche renvoient l'un à l'autre. Il ne prouve pas qu'une entreprise est légalement immatriculée, qu'un numéro d'immatriculation est authentique, ni que quiconque la recommande. Un outil qui n'a pas vérifié lui-même le répertoire ne doit pas présenter l'entreprise comme vérifiée. ABIZ ne garantit pas qu'un service d'IA trouvera, classera ou recommandera une entreprise.

## 6. Informations pratiques

### Trouver le numéro d'immatriculation

Le numéro RCI figure sur l'extrait du répertoire et sur les documents commerciaux. Le site du [RCI](https://www.rci.gouv.mc/) permet de consulter le répertoire.

### Ajouter l'enregistrement TXT

Ajoutez l'enregistrement là où le DNS de votre domaine est géré, en général chez votre bureau d'enregistrement ou votre hébergeur. Le registre des domaines en `.mc` est [NIC Monaco](https://nic.mc/), mais l'enregistrement s'ajoute chez votre bureau d'enregistrement ou votre fournisseur DNS ; tout fournisseur qui prend en charge les enregistrements TXT convient. Créez un enregistrement de type TXT nommé `_abiz` (certaines interfaces demandent le nom complet, `_abiz.rivierayachting.example`), avec la valeur exactement comme ci-dessus et un TTL de 300. N'ajoutez pas d'espaces dans la valeur et supprimez tout ancien enregistrement ABIZ pour qu'il n'en reste qu'un.

### Données personnelles et publication

La loi monégasque sur la protection des données personnelles s'applique aux données personnelles de votre fiche, par exemple le nom d'une personne à contacter. Si vous servez des clients dans l'Union européenne, le RGPD peut aussi s'appliquer. Tout ce que contient une fiche ABIZ est public : ne publiez que des informations destinées à l'être. Un entrepreneur individuel ne doit pas publier son adresse personnelle : la spécification exige d'omettre les adresses privées plutôt que de les marquer comme privées. Préférez une adresse générique comme `contact@` à une adresse électronique personnelle.

## 7. Pour aller plus loin

- [Spécification ABIZ (SPEC.md, en anglais)](../../../SPEC.md) : syntaxe DNS (section 3.1.1), clé `p` (section 3.3), clés d'entreprise (section 4.2)
- [Schéma JSON normatif](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Validateur de référence, scripts/validate.py](../../../scripts/validate.py)
- [Tous les guides pour l'Europe](index.md)
