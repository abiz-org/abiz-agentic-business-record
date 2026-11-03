# Devenir une entreprise agentique avec ABIZ au Sénégal

*Guide pour ABIZ 1.1 (proposition). La [spécification (SPEC.md, en anglais)](../../../SPEC.md) fait foi : si ce guide et la spécification diffèrent, c’est la spécification qui s’applique.* Le français est la langue officielle ; le wolof est la langue la plus parlée.

## 1. Ce que cela signifie pour une entreprise au Sénégal

On demande désormais souvent aux assistants d’IA « quel est le vrai site de cette société ? » ou « qui exploite ce commerce ? ». ABIZ (Agentic Business Record) est une norme ouverte qui permet à une entreprise établie au Sénégal de publier une seule fois ses informations publiques, sous une forme que ces outils savent lire : un court enregistrement DNS TXT sur un domaine que l’entreprise contrôle, qui pointe vers une fiche d’entreprise JSON servie en HTTPS. Comme ce pointeur se trouve dans le DNS de l’entreprise elle-même, un outil peut constater que la fiche a été publiée par la personne qui contrôle ce domaine, au lieu de se fier à un annuaire non officiel ou à une supposition.

## 2. Publier un enregistrement ABIZ

### Champs obligatoires

Toute fiche d’entreprise contient ces cinq champs (section 4.1 de la SPEC) :

| Champ | Exemple et règle |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | le nom public que connaissent les clients, par exemple `Thiof Dakar Traiteur` |
| `country` | `sn`, le code ISO 3166-1 alpha-2, en minuscules |
| `identity_host` | `thiofdakar.sn.to.co`, qui doit correspondre exactement à `h` dans le DNS |
| `domains` | `["thiofdakar.example"]`, qui doit inclure le domaine portant `_abiz` |

### Clé d’entreprise facultative `k`

`k` est facultative pour toute entreprise, immatriculée ou non. Si vous la publiez, elle doit être égale au champ `business_key` de la fiche, qui doit alors contenir aussi `registration_number`. Pour le Sénégal, la forme est :

```text
sn-<registration-number>
```

Le Sénégal n’utilise pas de subdivision : n’ajoutez ni code de région, ni code de ville. La section 4.2.2 de la SPEC n’exige une subdivision que pour les États-Unis, les sociétés provinciales canadiennes et les Émirats arabes unis, et l’interdit partout ailleurs.

**Quel numéro :** le numéro RCCM (Registre du commerce et du crédit mobilier) inscrit sur votre extrait d’immatriculation, tel que le greffe le délivre, lettres comprises. Il intègre le code du pays et celui du greffe : nous le traitons donc comme un numéro unique à l’échelle nationale. C’est notre lecture de la section 4.2.2 de la SPEC, qui ne cite pas les pays de l’OHADA ; elle reste à confirmer. Le format exact varie selon les greffes, par exemple `SN-DKR-2023-B-12345` pour Dakar.

**Normalisation (section 4.2.3 de la SPEC) :** partez du numéro tel que le registre le délivre, appliquez la normalisation Unicode NFKC, supprimez les espaces, `-`, `.`, `/` et les tirets, puis mettez les lettres en majuscules. Conservez les zéros initiaux et les préfixes en lettres. Le résultat ne doit contenir que des lettres et chiffres ASCII. Sinon, aucune clé d’entreprise n’est possible : omettez `k`, `business_key` et `registration_number`.

**Exemple (fictif) :** `SN-DKR-2023-B-12345` devient `SNDKR2023B12345`, donc `k=sn-SNDKR2023B12345`. Dans la fiche : `"business_key": "sn-SNDKR2023B12345"` et `"registration_number": "SNDKR2023B12345"`. Les clés se comparent sans tenir compte de la casse ; la forme canonique a le code pays en minuscules et le numéro en majuscules.

**À vérifier :** nous n’avons pas pu confirmer le format exact de ce numéro auprès d’une source officielle ; l’exemple n’est donc qu’indicatif. Utilisez le numéro tel qu’il figure sur votre document d’immatriculation officiel. S’il n’est pas clair quel numéro identifie votre entreprise au niveau national, n’indiquez pas `k` tant que vous n’en êtes pas sûr.

**Entrepreneurs individuels :** si le seul numéro dont vous disposez est un numéro personnel, comme un numéro d’identité nationale ou un identifiant fiscal personnel, ne publiez pas `k`. Omettez `k`, `business_key` et `registration_number` ; la fiche reste valide.

### Enregistrement DNS TXT

Publiez un seul enregistrement TXT à `_abiz` sous votre domaine, sous forme compacte, sans espaces, avec `v=abiz1` en premier :

```dns
_abiz.thiofdakar.example. 300 IN TXT "v=abiz1;k=sn-SNDKR2023B12345;h=thiofdakar.sn.to.co;p=gwdq74CEWKnAC3SZYyo5cZN7fRaDJyVW7CeJ3MWYS8o="
```

La valeur `p` ci-dessus est une clé d’exemple jetable, générée pour cette page. Ne la copiez jamais : publiez votre propre clé ou omettez `p`. Tous les noms, numéros et domaines de cette page sont fictifs.

Sans les balises facultatives `k` et `p`, ceci est également valide :

```dns
_abiz.thiofdakar.example. 300 IN TXT "v=abiz1;h=thiofdakar.sn.to.co;p=gwdq74CEWKnAC3SZYyo5cZN7fRaDJyVW7CeJ3MWYS8o="
```

La fiche d’entreprise servie en `application/json` à l’adresse `https://thiofdakar.sn.to.co` :

```json
{
  "record_version": "abiz1",
  "business_name": "Thiof Dakar Traiteur",
  "country": "sn",
  "business_key": "sn-SNDKR2023B12345",
  "registration_number": "SNDKR2023B12345",
  "identity_host": "thiofdakar.sn.to.co",
  "domains": [
    "thiofdakar.example"
  ],
  "public_key": "gwdq74CEWKnAC3SZYyo5cZN7fRaDJyVW7CeJ3MWYS8o=",
  "signature": "6mJPBz63jmYusZGGagCx3n5g0X2Spoj+lZeYpxu6jvz2L9aRjJslhOIPjiJHEayNF2DxhNFb3M0LFWVdhDR0AQ=="
}
```

Pour vérifier une fiche avant de la publier, lancez le validateur de référence depuis une copie de ce dépôt :

```sh
python scripts/validate.py record.json --domain thiofdakar.example --dns-value 'v=abiz1;k=sn-SNDKR2023B12345;h=thiofdakar.sn.to.co;p=gwdq74CEWKnAC3SZYyo5cZN7fRaDJyVW7CeJ3MWYS8o='
```

Vous pouvez héberger la fiche JSON vous-même, sur n’importe quel serveur HTTPS, ou passer par tout fournisseur compatible. ABIZ n’impose aucun fournisseur.

## 3. Passer par un fournisseur et MCP

Le Model Context Protocol (MCP) est un protocole ouvert qui permet aux assistants d’IA d’appeler des outils et de lire des données sur des serveurs externes de manière standard. Une fiche peut contenir un champ facultatif `mcp_server_url`, l’adresse HTTPS d’un serveur MCP de l’entreprise, par exemple pour des réservations ou des informations sur les produits. ABIZ ne garantit pas ce serveur : les outils doivent appliquer leurs propres contrôles d’accès (section 4.2.6 de la SPEC).

Un fournisseur peut héberger la fiche et publier le pointeur DNS pour vous. Par exemple, une société immatriculée au Sénégal dont la fiche est hébergée par to.co pourrait utiliser l’hôte `thiofdakar.sn.to.co`, ce qui donne la valeur DNS `v=abiz1;k=sn-SNDKR2023B12345;h=thiofdakar.sn.to.co;p=gwdq74CEWKnAC3SZYyo5cZN7fRaDJyVW7CeJ3MWYS8o=`. Une entreprise non immatriculée pourrait utiliser un hôte fondé sur sa ville, comme `thiofdakar-dakar.biz.to.co`. Tout fournisseur compatible, ou votre propre serveur, fonctionne de la même façon.

## 4. Clés et signatures (ABIZ 1.1)

ABIZ 1.1 ajoute une clé de signature facultative. La balise DNS `p` peut contenir une clé publique Ed25519 : 44 caractères en base64 standard, terminés par un seul `=` (section 3.3.2 de la SPEC). L’entreprise, ou un fournisseur agissant pour elle, conserve la clé privée correspondante et peut signer des contenus que d’autres vérifient avec la clé publiée. La clé privée appartient toujours à l’entreprise, et un hébergeur doit lui permettre de l’exporter.

- `p` est facultative. Si elle est présente, elle doit être une clé valide : toute autre valeur, comme un ancien jeton hexadécimal ABIZ 1.0 ou une clé en base64url, rend l’assertion entière invalide.
- Seule la clé en cours est publiée. Pour en changer, publiez la nouvelle clé dans `p` ; pour la révoquer, supprimez `p`. Les clés retirées ne sont pas publiées en ABIZ 1.1, ni dans le DNS, ni dans la fiche.
- Une clé montre qui contrôle le DNS du domaine. Elle ne prouve pas l’identité juridique.

## 5. Ce que verront les outils d’IA

Un outil compatible qui lit votre fiche peut répondre à des questions comme :

1. Quel est le site officiel de Thiof Dakar Traiteur ?
2. Quels domaines appartiennent à cette entreprise ?
3. Quel numéro d’immatriculation l’entreprise indique-t-elle, et dans quel pays ?
4. Que propose-t-elle, et quand est-elle ouverte ?

**Limites :** ABIZ montre ce que le titulaire d’un domaine a publié. Cela ne prouve pas que l’entreprise est légalement immatriculée, que son numéro est authentique, ni qu’un service d’IA, une administration ou un fournisseur la recommande. Lorsque c’est important, outils et personnes doivent consulter le registre officiel.

## 6. Notes pratiques locales

- **Registre :** le Registre du commerce et du crédit mobilier (RCCM), tenu par les greffes des tribunaux de commerce ; l’APIX accompagne la création d’entreprise. Les entreprises ont aussi un NINEA (identifiant fiscal). Nous n’indiquons pas de site, faute d’avoir pu confirmer une adresse officielle qui fonctionne.
- **Ajouter l’enregistrement TXT :** dans les réglages DNS de votre bureau d’enregistrement ou de votre hébergeur DNS, ajoutez un enregistrement TXT nommé `_abiz` (certaines interfaces demandent le nom complet, `_abiz.votredomaine.sn`), avec la valeur ci-dessus et une durée de vie (TTL) de 300 secondes. Les domaines en `.sn` fonctionnent comme les `.com` ou tout autre domaine. Gardez la valeur d’un seul tenant si possible, et ne coupez jamais `p`.
- **Données personnelles :** Loi n° 2008-12 du 25 janvier 2008 sur la protection des données à caractère personnel, contrôlée par la CDP. Une fiche ABIZ est publique. Ne publiez que des informations professionnelles que vous acceptez de partager, et omettez les adresses personnelles et les numéros de téléphone privés (section 4.3 de la SPEC).

## 7. Pour aller plus loin

- [Spécification ABIZ (SPEC.md, en anglais)](../../../SPEC.md)
- [Schéma JSON de la fiche d’entreprise](../../../schemas/abiz-business-record-v1.schema.json)
- [Validateur de référence](../../../scripts/validate.py)
- [Guides ABIZ par pays : Afrique](index.md)
