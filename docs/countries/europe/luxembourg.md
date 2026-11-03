# Devenir une entreprise agentique avec ABIZ au Luxembourg

*Guide pour ABIZ 1.1 (proposition). Le texte de référence est la [spécification (SPEC.md, en anglais)](../../../SPEC.md) : en cas de divergence entre ce guide et la spécification, la spécification prévaut.* Le Luxembourg a trois langues administratives ; ce guide est en français, la langue la plus utilisée pour les démarches d'entreprise. Il n'existe pas encore de version en luxembourgeois ou en allemand.

## 1. Ce que cela signifie pour une entreprise au Luxembourg

On interroge de plus en plus les assistants d'IA sur les entreprises : qui elles sont, ce qu'elles proposent, où les trouver. ABIZ (Agentic Business Record) permet à une entreprise de publier une fiche publique, lisible par les machines, avec ses propres informations (nom, pays, site web, services, horaires) et, sur son propre domaine, un enregistrement DNS qui pointe vers cette fiche.

Seule l'entreprise, ou une personne qu'elle mandate, peut modifier le DNS de son domaine. Un logiciel compatible peut donc trouver la fiche à partir du domaine et vérifier que le domaine et la fiche renvoient l'un à l'autre, au lieu de reconstituer les informations à partir de pages web éparses. ABIZ est ouvert et indépendant de tout fournisseur : aucune adhésion, aucun frais ni aucun fournisseur particulier n'est requis.

## 2. Publier une fiche ABIZ

### Champs obligatoires

La fiche d'entreprise est un document JSON qui doit être conforme au [schéma normatif](../../../schemas/abiz-business-record-v1.schema.json). Cinq champs sont obligatoires :

| Champ | Exemple | Remarques |
| --- | --- | --- |
| `record-version` | `abiz1` | Toujours cette valeur |
| `business-name` | `Moselle Conseil S.à r.l.` | Le nom public, en général tel qu'il figure au registre, avec la forme juridique si vous l'utilisez |
| `country` | `lu` | Code pays ISO 3166-1 alpha-2 ; la forme canonique est en minuscules |
| `identity-host` | `moselleconseil.lu.to.co` | Exactement la valeur DNS `h` : un nom d'hôte avec un chemin facultatif, sans `https://` |
| `domains` | `["moselleconseil.example"]` | Les domaines revendiqués par la fiche, y compris celui qui porte `_abiz` |

### Clé d'entreprise `k` (facultative)

`k` est facultatif pour toute entreprise, immatriculée ou non. Si vous le publiez, la fiche doit aussi contenir `business-key` et `registration-number`, et `k` doit être égal à `business-key`.

Au Luxembourg, la clé s'écrit `lu-` suivi du numéro d'immatriculation, sans subdivision : une clé comportant une partie intermédiaire, comme `lu-xx-…`, est invalide.

- **Registre :** Registre de commerce et des sociétés (RCS), tenu par le [Luxembourg Business Registers (LBR)](https://www.lbr.lu/)
- **Numéro à utiliser :** le numéro RCS, avec sa lettre (par exemple `B` pour une société commerciale)
- **Écriture :** partez du numéro tel que le registre l'attribue, appliquez la normalisation Unicode NFKC, supprimez les espaces, `-`, `.`, `/` et les autres tirets, puis mettez les lettres en majuscules. Les zéros initiaux et les préfixes en lettres sont conservés. Le résultat ne doit contenir que des lettres et des chiffres ASCII.

Exemple (numéro fictif) : `B123456` est déjà sous forme canonique. La fiche contient alors `"registration-number": "B123456"` et `"business-key": "lu-B123456"`, et le DNS porte `k=lu-B123456`. Conservez la lettre initiale.

Les clés se comparent sans tenir compte de la casse, mais publiez la forme canonique : code pays en minuscules, numéro en majuscules.

### Enregistrement DNS TXT

Publiez un seul enregistrement TXT ABIZ sous `_abiz` sur votre domaine, sous forme compacte, sans espaces :

```dns
_abiz.moselleconseil.example. 300 IN TXT "v=abiz1;k=lu-B123456;h=moselleconseil.lu.to.co;p=5DdRuj6PRmyneE8oAVfLmXzA2kP+KG3l0nh0hM9DIOw="
```

- `v=abiz1` doit venir en premier. `h` est obligatoire ; `k` et `p` sont facultatifs.
- Les noms de balises sont en minuscules et sensibles à la casse. Une balise ne doit pas apparaître deux fois.
- Une durée de vie (TTL) de 300 secondes est recommandée.

La valeur `p` ci-dessus est une clé d'exemple jetable. Ne la copiez jamais : publiez votre propre clé ou omettez `p`.

### Fiche d'entreprise (JSON)

La fiche servie à l'adresse `https://moselleconseil.lu.to.co`, au format `application/json` :

```json
{
  "record-version": "abiz1",
  "business-name": "Moselle Conseil S.à r.l.",
  "country": "lu",
  "business-key": "lu-B123456",
  "registration-number": "B123456",
  "identity-host": "moselleconseil.lu.to.co",
  "domains": [
    "moselleconseil.example"
  ],
  "description": "Cabinet de conseil à Luxembourg.",
  "website": "https://moselleconseil.example",
  "locations": [
    {
      "kind": "trading",
      "city": "Luxembourg",
      "country": "lu",
      "public": true
    }
  ]
}
```

Le validateur de référence vérifie localement la fiche et la valeur DNS :

```sh
python scripts/validate.py record.json --domain moselleconseil.example --dns-value 'v=abiz1;k=lu-B123456;h=moselleconseil.lu.to.co;p=5DdRuj6PRmyneE8oAVfLmXzA2kP+KG3l0nh0hM9DIOw='
```

### Hébergement par vous-même ou par un fournisseur

Vous pouvez servir la fiche vous-même sur tout hôte HTTPS que vous contrôlez, ou passer par n'importe quel fournisseur compatible. ABIZ n'impose ni fournisseur ni schéma de nom d'hôte. Dans tous les cas, la fiche doit être servie en HTTPS et vous devez contrôler le domaine qui porte `_abiz`.

## 3. Fournisseurs et MCP

MCP (Model Context Protocol) est un protocole ouvert qui permet aux assistants d'IA d'appeler des outils et de lire des données sur des serveurs externes. Un fournisseur peut exploiter un serveur MCP grâce auquel un assistant obtient directement votre fiche publique. Vous pouvez l'indiquer dans le champ facultatif `mcp-server-url`. ABIZ n'exige pas de serveur MCP, et un outil ne doit pas en appeler un automatiquement au seul motif qu'il figure dans une fiche.

Par exemple, un fournisseur peut servir votre fiche à l'adresse `moselleconseil.lu.to.co` et exploiter un serveur MCP. Un assistant connecté à ce serveur peut alors demander les horaires ou les services de Moselle Conseil S.à r.l. et obtenir les informations de votre fiche, au lieu de les deviner.

## 4. Clés et signatures (ABIZ 1.1)

ABIZ 1.1 permet de publier une clé publique Ed25519 dans la balise DNS `p`. `p` est facultatif. S'il est présent, il doit s'agir de l'encodage base64 standard de la clé de 32 octets : 44 caractères terminés par un seul `=`, dans une seule chaîne DNS. Toute autre valeur, comme un jeton hexadécimal ABIZ 1.0 ou une clé en base64url, rend l'ensemble de l'enregistrement invalide.

La clé privée correspondante appartient à l'entreprise et n'est jamais publiée. Un fournisseur qui la conserve pour vous doit vous permettre de l'exporter. Un logiciel peut vérifier une signature produite avec la clé privée à l'aide de la clé publiée dans le DNS. ABIZ 1.1 ne définit pas encore quels octets une signature de la fiche couvre.

Pour changer de clé, publiez-en une nouvelle dans `p` ; pour la révoquer, supprimez `p`. Les clés retirées ne sont pas publiées en ABIZ 1.1, ni dans le DNS ni dans la fiche. La clé montre quelle clé le titulaire du domaine a publiée ; elle ne prouve pas l'identité juridique.

## 5. Ce que voient les outils d'IA

Avec une fiche valide, un assistant compatible peut répondre à des questions comme :

- « Moselle Conseil S.à r.l. est-elle une entreprise située à Luxembourg ? »
- « Que propose Moselle Conseil S.à r.l., et quels sont ses horaires ? »
- « moselleconseil.example est-il le site officiel de Moselle Conseil S.à r.l. ? »
- « Quel numéro d'immatriculation Moselle Conseil S.à r.l. indique-t-elle pour elle-même ? »

Les limites comptent. ABIZ montre qu'un domaine et une fiche renvoient l'un à l'autre. Il ne prouve pas qu'une entreprise est légalement immatriculée, qu'un numéro d'immatriculation est authentique, ni que quiconque la recommande. Un outil qui n'a pas vérifié lui-même le registre ne doit pas présenter l'entreprise comme vérifiée. ABIZ ne garantit pas qu'un service d'IA trouvera, classera ou recommandera une entreprise.

## 6. Informations pratiques

### Trouver le numéro d'immatriculation

Le numéro RCS figure sur l'extrait du registre et sur les documents de la société. La recherche est possible sur le site du [LBR](https://www.lbr.lu/).

### Ajouter l'enregistrement TXT

Ajoutez l'enregistrement là où le DNS de votre domaine est géré, en général chez votre bureau d'enregistrement ou votre hébergeur. Le registre des domaines en `.lu` est [DNS-LU](https://www.dns.lu/), mais l'enregistrement s'ajoute chez votre bureau d'enregistrement ou votre fournisseur DNS ; tout fournisseur qui prend en charge les enregistrements TXT convient. Créez un enregistrement de type TXT nommé `_abiz` (certaines interfaces demandent le nom complet, `_abiz.moselleconseil.example`), avec la valeur exactement comme ci-dessus et un TTL de 300. N'ajoutez pas d'espaces dans la valeur et supprimez tout ancien enregistrement ABIZ pour qu'il n'en reste qu'un.

### Données personnelles et publication

Le RGPD s'applique aux données personnelles de votre fiche, par exemple le nom d'un entrepreneur individuel ou d'une personne à contacter. Le [Comité européen de la protection des données](https://www.edpb.europa.eu/) renvoie vers chaque autorité nationale. Tout ce que contient une fiche ABIZ est public : ne publiez que des informations destinées à l'être. Un entrepreneur individuel ne doit pas publier son adresse personnelle : la spécification exige d'omettre les adresses privées plutôt que de les marquer comme privées. Préférez une adresse générique comme `contact@` à une adresse électronique personnelle.

## 7. Pour aller plus loin

- [Spécification ABIZ (SPEC.md, en anglais)](../../../SPEC.md) : syntaxe DNS (section 3.1.1), clé `p` (section 3.3), clés d'entreprise (section 4.2)
- [Schéma JSON normatif](../../../schemas/abiz-business-record-v1.schema.json)
- [Validateur de référence, scripts/validate.py](../../../scripts/validate.py)
- [Tous les guides pour l'Europe](index.md)
