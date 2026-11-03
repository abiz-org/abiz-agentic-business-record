# Devenir une entreprise agentique avec ABIZ au Togo

*Guide pour ABIZ 1.1 (proposition). La [spécification (SPEC.md, en anglais)](../../../SPEC.md) fait foi : si ce guide et la spécification diffèrent, c’est la spécification qui s’applique.* Le français est la langue officielle ; l’éwé et le kabiyè sont très parlés.

## 1. Ce que cela signifie pour une entreprise au Togo

On demande désormais souvent aux assistants d’IA « quel est le vrai site de cette société ? » ou « qui exploite ce commerce ? ». ABIZ (Agentic Business Record) est une norme ouverte qui permet à une entreprise établie au Togo de publier une seule fois ses informations publiques, sous une forme que ces outils savent lire : un court enregistrement DNS TXT sur un domaine que l’entreprise contrôle, qui pointe vers une fiche d’entreprise JSON servie en HTTPS. Comme ce pointeur se trouve dans le DNS de l’entreprise elle-même, un outil peut constater que la fiche a été publiée par la personne qui contrôle ce domaine, au lieu de se fier à un annuaire non officiel ou à une supposition.

## 2. Publier un enregistrement ABIZ

### Champs obligatoires

Toute fiche d’entreprise contient ces cinq champs (section 4.1 de la SPEC) :

| Champ | Exemple et règle |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | le nom public que connaissent les clients, par exemple `Pagnes de Lomé` |
| `country` | `tg`, le code ISO 3166-1 alpha-2, en minuscules |
| `identity_host` | `pagneslome.tg.to.co`, qui doit correspondre exactement à `h` dans le DNS |
| `domains` | `["pagneslome.example"]`, qui doit inclure le domaine portant `_abiz` |

### Clé d’entreprise facultative `k`

`k` est facultative pour toute entreprise, immatriculée ou non. Si vous la publiez, elle doit être égale au champ `business_key` de la fiche, qui doit alors contenir aussi `registration_number`. Pour le Togo, la forme est :

```text
tg-<registration-number>
```

Le Togo n’utilise pas de subdivision : n’ajoutez ni code de région, ni code de ville. La section 4.2.2 de la SPEC n’exige une subdivision que pour les États-Unis, les sociétés provinciales canadiennes et les Émirats arabes unis, et l’interdit partout ailleurs.

**Quel numéro :** le numéro RCCM (Registre du commerce et du crédit mobilier) inscrit sur votre extrait d’immatriculation, tel que le greffe le délivre, lettres comprises. Il intègre le code du pays et celui du greffe : nous le traitons donc comme un numéro unique à l’échelle nationale. C’est notre lecture de la section 4.2.2 de la SPEC, qui ne cite pas les pays de l’OHADA ; elle reste à confirmer. Le format exact varie selon les greffes, par exemple `TG-LFW-01-2023-B12-01234` pour Lomé.

**Normalisation (section 4.2.3 de la SPEC) :** partez du numéro tel que le registre le délivre, appliquez la normalisation Unicode NFKC, supprimez les espaces, `-`, `.`, `/` et les tirets, puis mettez les lettres en majuscules. Conservez les zéros initiaux et les préfixes en lettres. Le résultat ne doit contenir que des lettres et chiffres ASCII. Sinon, aucune clé d’entreprise n’est possible : omettez `k`, `business_key` et `registration_number`.

**Exemple (fictif) :** `TG-LFW-01-2023-B12-01234` devient `TGLFW012023B1201234`, donc `k=tg-TGLFW012023B1201234`. Dans la fiche : `"business_key": "tg-TGLFW012023B1201234"` et `"registration_number": "TGLFW012023B1201234"`. Les clés se comparent sans tenir compte de la casse ; la forme canonique a le code pays en minuscules et le numéro en majuscules.

**À vérifier :** nous n’avons pas pu confirmer le format exact de ce numéro auprès d’une source officielle ; l’exemple n’est donc qu’indicatif. Utilisez le numéro tel qu’il figure sur votre document d’immatriculation officiel. S’il n’est pas clair quel numéro identifie votre entreprise au niveau national, n’indiquez pas `k` tant que vous n’en êtes pas sûr.

**Entrepreneurs individuels :** si le seul numéro dont vous disposez est un numéro personnel, comme un numéro d’identité nationale ou un identifiant fiscal personnel, ne publiez pas `k`. Omettez `k`, `business_key` et `registration_number` ; la fiche reste valide.

### Enregistrement DNS TXT

Publiez un seul enregistrement TXT à `_abiz` sous votre domaine, sous forme compacte, sans espaces, avec `v=abiz1` en premier :

```dns
_abiz.pagneslome.example. 300 IN TXT "v=abiz1;k=tg-TGLFW012023B1201234;h=pagneslome.tg.to.co;p=daXV8kIwQT1k1YR/fH//vPKlh7CtIFfhdnDPnAqipZY="
```

La valeur `p` ci-dessus est une clé d’exemple jetable, générée pour cette page. Ne la copiez jamais : publiez votre propre clé. Une assertion ABIZ 1.1 doit inclure `p`. Tous les noms, numéros et domaines de cette page sont fictifs.

Sans la balise facultative `k`, ceci est également valide :

```dns
_abiz.pagneslome.example. 300 IN TXT "v=abiz1;h=pagneslome.tg.to.co;p=daXV8kIwQT1k1YR/fH//vPKlh7CtIFfhdnDPnAqipZY="
```

La fiche d’entreprise servie en `application/json` à l’adresse `https://pagneslome.tg.to.co` :

```json
{
  "record_version": "abiz1",
  "business_name": "Pagnes de Lomé",
  "country": "tg",
  "business_key": "tg-TGLFW012023B1201234",
  "registration_number": "TGLFW012023B1201234",
  "identity_host": "pagneslome.tg.to.co",
  "domains": [
    "pagneslome.example"
  ],
  "public_key": "daXV8kIwQT1k1YR/fH//vPKlh7CtIFfhdnDPnAqipZY=",
  "signature": "eGbmvKP06hr39vUKLFKWr1Oom+/bcKFdNX8v0stofIROrA36ART8r1ZlvBLaE0q8cuTcsZ4/AaTkYHE4r+dzAQ=="
}
```

Pour vérifier une fiche avant de la publier, lancez le validateur de référence depuis une copie de ce dépôt :

```sh
python scripts/validate.py record.json --domain pagneslome.example --dns-value 'v=abiz1;k=tg-TGLFW012023B1201234;h=pagneslome.tg.to.co;p=daXV8kIwQT1k1YR/fH//vPKlh7CtIFfhdnDPnAqipZY='
```

Vous pouvez héberger la fiche JSON vous-même, sur n’importe quel serveur HTTPS, ou passer par tout fournisseur compatible. ABIZ n’impose aucun fournisseur.

## 3. Passer par un fournisseur et MCP

Le Model Context Protocol (MCP) est un protocole ouvert qui permet aux assistants d’IA d’appeler des outils et de lire des données sur des serveurs externes de manière standard. Une fiche peut contenir un champ facultatif `mcp_server_url`, l’adresse HTTPS d’un serveur MCP de l’entreprise, par exemple pour des réservations ou des informations sur les produits. ABIZ ne garantit pas ce serveur : les outils doivent appliquer leurs propres contrôles d’accès (section 4.2.6 de la SPEC).

Un fournisseur peut héberger la fiche et publier le pointeur DNS pour vous. Par exemple, une société immatriculée au Togo dont la fiche est hébergée par to.co pourrait utiliser l’hôte `pagneslome.tg.to.co`, ce qui donne la valeur DNS `v=abiz1;k=tg-TGLFW012023B1201234;h=pagneslome.tg.to.co;p=daXV8kIwQT1k1YR/fH//vPKlh7CtIFfhdnDPnAqipZY=`. Une entreprise non immatriculée pourrait utiliser un hôte fondé sur sa ville, comme `pagneslome-lome.biz.to.co`. Tout fournisseur compatible, ou votre propre serveur, fonctionne de la même façon.

## 4. Clés et signatures (ABIZ 1.1)

ABIZ 1.1 exige une clé de signature. La balise DNS `p` contient une clé publique Ed25519 : 32 octets bruts, en base64 standard, 44 caractères, un seul `=` final (section 3.3.2 de la SPEC). Le base64url n’est pas accepté. L’entreprise, ou un fournisseur agissant pour elle, conserve la clé privée correspondante et signe la fiche avec elle. La clé privée appartient toujours à l’entreprise, et un hébergeur doit lui permettre de l’exporter.

- `v` et `h` sont obligatoires. `p` est obligatoire. `k` est facultative. `p` doit être une clé valide : toute autre valeur, comme un ancien jeton hexadécimal ABIZ 1.0 ou une clé en base64url, rend l’assertion entière invalide.
- Seule la clé en cours est publiée. Pour en changer, générez une nouvelle paire Ed25519, publiez la nouvelle clé publique dans l’assertion DNS ou well-known, resignez la fiche avec la nouvelle clé privée, et faites correspondre `public_key` à ce `p`. Tenez compte du cache et de la propagation DNS. Supprimer seulement `p` n’est pas une révocation valable tant que l’assertion ABIZ 1.1 reste en place : pour la retirer, supprimez toute la déclaration DNS ou well-known. Les clés retirées ne sont pas publiées en ABIZ 1.1, ni dans le DNS, ni dans la fiche.
- Une clé montre qui contrôle le DNS du domaine. Elle ne prouve pas l’identité juridique.

## 5. Ce que verront les outils d’IA

Un outil compatible qui lit votre fiche peut répondre à des questions comme :

1. Quel est le site officiel de Pagnes de Lomé ?
2. Quels domaines appartiennent à cette entreprise ?
3. Quel numéro d’immatriculation l’entreprise indique-t-elle, et dans quel pays ?
4. Que propose-t-elle, et quand est-elle ouverte ?

**Limites :** ABIZ montre ce que le titulaire d’un domaine a publié. Cela ne prouve pas que l’entreprise est légalement immatriculée, que son numéro est authentique, ni qu’un service d’IA, une administration ou un fournisseur la recommande. Lorsque c’est important, outils et personnes doivent consulter le registre officiel.

## 6. Notes pratiques locales

- **Registre :** le Registre du commerce et du crédit mobilier (RCCM), tenu par les greffes des tribunaux ; le Centre de formalités des entreprises (CFE) sert de guichet unique. Site officiel : <https://www.cfetogo.tg>.
- **Ajouter l’enregistrement TXT :** dans les réglages DNS de votre bureau d’enregistrement ou de votre hébergeur DNS, ajoutez un enregistrement TXT nommé `_abiz` (certaines interfaces demandent le nom complet, `_abiz.votredomaine.tg`), avec la valeur ci-dessus et une durée de vie (TTL) de 300 secondes. Les domaines en `.tg` fonctionnent comme les `.com` ou tout autre domaine. Gardez la valeur d’un seul tenant si possible, et ne coupez jamais `p`.
- **Données personnelles :** Vérifiez les règles de protection des données applicables au Togo avant de publier des données personnelles. Une fiche ABIZ est publique. Ne publiez que des informations professionnelles que vous acceptez de partager, et omettez les adresses personnelles et les numéros de téléphone privés (section 4.3 de la SPEC).

## 7. Pour aller plus loin

- [Spécification ABIZ (SPEC.md, en anglais)](../../../SPEC.md)
- [Schéma JSON de la fiche d’entreprise](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Validateur de référence](../../../scripts/validate.py)
- [Guides ABIZ par pays : Afrique](index.md)
