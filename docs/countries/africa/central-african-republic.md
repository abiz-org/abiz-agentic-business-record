# Devenir une entreprise agentique avec ABIZ en République centrafricaine

## 1. Ce que cela signifie pour une entreprise en République centrafricaine

On demande désormais souvent aux assistants d’IA « quel est le vrai site de cette société ? » ou « qui exploite ce commerce ? ». ABIZ (Agentic Business Record) est une norme ouverte qui permet à une entreprise établie en République centrafricaine de publier une seule fois ses informations publiques, sous une forme que ces outils savent lire : un court enregistrement DNS TXT sur un domaine que l’entreprise contrôle, qui pointe vers une fiche d’entreprise JSON servie en HTTPS. Comme ce pointeur se trouve dans le DNS de l’entreprise elle-même, un outil peut constater que la fiche a été publiée par la personne qui contrôle ce domaine, au lieu de se fier à un annuaire non officiel ou à une supposition.

## 2. Publier un enregistrement ABIZ

### Champs obligatoires

Toute fiche d’entreprise contient ces cinq champs (section 4.1 de la SPEC) :

| Champ | Exemple et règle |
|---|---|
| `record-version` | `abiz1` |
| `business-name` | le nom public que connaissent les clients, par exemple `Menuiserie Oubangui` |
| `country` | `cf`, le code ISO 3166-1 alpha-2, en minuscules |
| `identity-host` | `www.menuiserieoubangui.example/abiz`, qui doit correspondre exactement à `h` dans le DNS |
| `domains` | `["menuiserieoubangui.example"]`, qui doit inclure le domaine portant `_abiz` |

Une fiche minimale :

```json
{
  "record-version": "abiz1",
  "business-name": "Menuiserie Oubangui",
  "country": "cf",
  "identity-host": "www.menuiserieoubangui.example/abiz",
  "domains": [
    "menuiserieoubangui.example"
  ]
}
```

### Clé d’entreprise facultative `k`

`k` est facultative pour toute entreprise, immatriculée ou non. Si vous la publiez, elle doit être égale au champ `business-key` de la fiche, qui doit alors contenir aussi `registration-number`. Pour la République centrafricaine, la forme est :

```text
cf-<registration-number>
```

La République centrafricaine n’utilise pas de subdivision : n’ajoutez ni code de région, ni code de ville. La section 4.2.2 de la SPEC n’exige une subdivision que pour les États-Unis, les sociétés provinciales canadiennes et les Émirats arabes unis, et l’interdit partout ailleurs.

**Quel numéro :** le numéro RCCM (Registre du commerce et du crédit mobilier) inscrit sur votre extrait d’immatriculation, tel que le greffe le délivre, lettres comprises. Il intègre le code du pays et celui du greffe : nous le traitons donc comme un numéro unique à l’échelle nationale. C’est notre lecture de la section 4.2.2 de la SPEC, qui ne cite pas les pays de l’OHADA ; elle reste à confirmer. Le format exact varie selon les greffes, par exemple `CA/BG/2023/B/123` pour Bangui.

**Normalisation (section 4.2.3 de la SPEC) :** partez du numéro tel que le registre le délivre, appliquez la normalisation Unicode NFKC, supprimez les espaces, `-`, `.`, `/` et les tirets, puis mettez les lettres en majuscules. Conservez les zéros initiaux et les préfixes en lettres. Le résultat ne doit contenir que des lettres et chiffres ASCII. Sinon, aucune clé d’entreprise n’est possible : omettez `k`, `business-key` et `registration-number`.

**Exemple (fictif) :** `CA/BG/2023/B/123` devient `CABG2023B123`, donc `k=cf-CABG2023B123`. Dans la fiche : `"business-key": "cf-CABG2023B123"` et `"registration-number": "CABG2023B123"`. Les clés se comparent sans tenir compte de la casse ; la forme canonique a le code pays en minuscules et le numéro en majuscules.

```json
{
  "record-version": "abiz1",
  "business-name": "Menuiserie Oubangui",
  "country": "cf",
  "business-key": "cf-CABG2023B123",
  "registration-number": "CABG2023B123",
  "identity-host": "www.menuiserieoubangui.example/abiz",
  "domains": [
    "menuiserieoubangui.example"
  ]
}
```

**À vérifier :** nous n’avons pas pu confirmer le format exact de ce numéro auprès d’une source officielle ; l’exemple n’est donc qu’indicatif. Utilisez le numéro tel qu’il figure sur votre document d’immatriculation officiel. S’il n’est pas clair quel numéro identifie votre entreprise au niveau national, n’indiquez pas `k` tant que vous n’en êtes pas sûr.

### Enregistrement DNS TXT

Publiez un seul enregistrement TXT à `_abiz` sous votre domaine, sous forme compacte, sans espaces, avec `v=abiz1` en premier :

```dns
_abiz.menuiserieoubangui.example. 300 IN TXT "v=abiz1;k=cf-CABG2023B123;h=www.menuiserieoubangui.example/abiz;p=oS5YhE6Qz35Id1hMp3XOI3eQWW03DVgY3kU6rEdlodQ="
```

Sans les balises facultatives `k` et `p`, ceci est également valide :

```dns
_abiz.menuiserieoubangui.example. 300 IN TXT "v=abiz1;h=www.menuiserieoubangui.example/abiz"
```

Tous les noms et numéros de cette page sont fictifs. La valeur `p` est la clé d’exemple jetable de la spécification, pas une vraie clé.

Vous pouvez héberger la fiche JSON vous-même, sur n’importe quel serveur HTTPS, ou passer par tout fournisseur compatible. ABIZ n’impose aucun fournisseur.

Pour vérifier une fiche avant de la publier, lancez le validateur de référence depuis une copie de ce dépôt :

```sh
python scripts/validate.py record.json --domain menuiserieoubangui.example --dns-value "v=abiz1;k=cf-CABG2023B123;h=www.menuiserieoubangui.example/abiz;p=oS5YhE6Qz35Id1hMp3XOI3eQWW03DVgY3kU6rEdlodQ="
```

## 3. Passer par un fournisseur et MCP

Le Model Context Protocol (MCP) est un protocole ouvert qui permet aux assistants d’IA d’appeler des outils et de lire des données sur des serveurs externes de manière standard. Une fiche peut contenir un champ facultatif `mcp-server-url`, l’adresse HTTPS d’un serveur MCP de l’entreprise, par exemple pour des réservations ou des informations sur les produits. ABIZ ne garantit pas ce serveur : les outils doivent appliquer leurs propres contrôles d’accès (section 4.2.6 de la SPEC).

Un fournisseur peut héberger la fiche et publier le pointeur DNS pour vous. Par exemple, une société immatriculée en République centrafricaine dont la fiche est hébergée par to.co pourrait utiliser l’hôte `menuiserieoubangui.cf.to.co`, ce qui donne la valeur DNS `v=abiz1;k=cf-CABG2023B123;h=menuiserieoubangui.cf.to.co`. Une entreprise non immatriculée pourrait utiliser un hôte fondé sur sa ville, comme `menuiserieoubangui-bangui.biz.to.co`. Tout fournisseur compatible, ou votre propre serveur, fonctionne de la même façon.

## 4. Clés et signatures (ABIZ 1.1)

ABIZ 1.1 ajoute une clé de signature facultative. La balise DNS `p` peut contenir une clé publique Ed25519 : 44 caractères en base64 standard, terminés par un seul `=` (section 3.3.2 de la SPEC). L’entreprise, ou un fournisseur agissant pour elle, conserve la clé privée correspondante et peut signer des contenus que d’autres vérifient avec la clé publiée. La clé privée appartient toujours à l’entreprise, et un hébergeur doit lui permettre de l’exporter.

- `p` est facultative. Si elle est présente, elle doit être une clé valide : toute autre valeur, comme un ancien jeton hexadécimal ABIZ 1.0 ou une clé en base64url, rend l’assertion entière invalide.
- Seule la clé en cours est publiée. Pour en changer, publiez la nouvelle clé dans `p` ; pour la révoquer, supprimez `p`. Les clés retirées ne sont pas publiées en ABIZ 1.1, ni dans le DNS, ni dans la fiche.
- Une clé montre qui contrôle le DNS du domaine. Elle ne prouve pas l’identité juridique.

## 5. Ce que verront les outils d’IA

Un outil compatible qui lit votre fiche peut répondre à des questions comme :

1. Quel est le site officiel de Menuiserie Oubangui ?
2. Quels domaines appartiennent à cette entreprise ?
3. Quel numéro d’immatriculation l’entreprise indique-t-elle, et dans quel pays ?
4. Que propose-t-elle, et quand est-elle ouverte ?

**Limites :** ABIZ montre ce que le titulaire d’un domaine a publié. Cela ne prouve pas que l’entreprise est légalement immatriculée, que son numéro est authentique, ni qu’un service d’IA, une administration ou un fournisseur la recommande. Lorsque c’est important, outils et personnes doivent consulter le registre officiel.

## 6. Notes pratiques locales

- **Registre :** le Registre du commerce et du crédit mobilier (RCCM), tenu par les greffes des tribunaux ; le Guichet unique de formalités des entreprises accompagne les créations. Nous n’indiquons pas de site, faute d’avoir pu confirmer une adresse officielle qui fonctionne.
- **Ajouter l’enregistrement TXT :** dans les réglages DNS de votre bureau d’enregistrement ou de votre hébergeur DNS, ajoutez un enregistrement TXT nommé `_abiz` (certaines interfaces demandent le nom complet, `_abiz.votredomaine.cf`), avec la valeur ci-dessus et une durée de vie (TTL) de 300 secondes. Les domaines en `.cf` fonctionnent comme les `.com` ou tout autre domaine. Gardez la valeur d’un seul tenant si possible, et ne coupez jamais `p`.
- **Données personnelles :** Vérifiez les règles de protection des données applicables en République centrafricaine avant de publier des données personnelles. Une fiche ABIZ est publique. Ne publiez que des informations professionnelles que vous acceptez de partager, et omettez les adresses personnelles et les numéros de téléphone privés (section 4.3 de la SPEC).
- **Langues :** Le français et le sango sont langues officielles.

## 7. Pour aller plus loin

- [Spécification ABIZ (SPEC.md, en anglais)](../../../SPEC.md)
- [Schéma JSON de la fiche d’entreprise](../../../schemas/abiz-business-record-v1.schema.json)
- [Validateur de référence](../../../scripts/validate.py)
- [Guides ABIZ par pays : Afrique](index.md)
