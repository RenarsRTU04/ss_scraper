# Nesisto auto meklētājs ss.com sludinājumos

## Projekta uzdevums

Šī Python programma ir izstrādāta, lai palīdzētu lietotājiem atrast nesistus automobiļus ss.com sludinājumu portālā, balstoties uz konkrēta sistā auto sludinājuma datiem. Lietotājs ievada saiti uz ss.com sludinājumu, kurā aprakstīts sists auto. Programma automātiski nolasa šī auto marku, modeli, izlaiduma gadu, dzinēja tipu, nobraukumu un cenu. Pēc tam tā veic meklēšanu ss.com portālā, lai atrastu tādas pašas markas un modeļa automašīnas, kas nav sistas, un izvada šo sludinājumu saites, kā arī veic cenu salīdzinājumu. Visi rezultāti tiek pārskatāmi izvadīti tabulas veidā un saglabāti CSV failā, lai lietotājs varētu tos analizēt arī vēlāk.

Projekta galvenais uzdevums ir atvieglot auto pircēju darbu, ļaujot ātri un ērti salīdzināt sistā auto cenu ar līdzīgu, bet nesistu auto cenām tirgū. Tas palīdz pieņemt pamatotākus lēmumus par auto iegādi vai pārdošanu, kā arī sniedz pārskatāmu informāciju par tirgus situāciju konkrētajam auto modelim un markai.

## Izmantotās Python bibliotēkas un to pielietojums

Šajā projektā tiek izmantotas vairākas populāras Python bibliotēkas, kas nodrošina efektīvu datu iegūšanu, apstrādi un attēlošanu:

### **requests**

Šī bibliotēka tiek izmantota, lai veiktu HTTP pieprasījumus un iegūtu ss.com sludinājumu lapu HTML saturu. Tā ļauj ērti un droši lejupielādēt nepieciešamos datus no interneta.

### **beautifulsoup4**

Šī bibliotēka tiek izmantota HTML dokumentu parsēšanai un nepieciešamās informācijas (piemēram, auto markas, modeļa, cenas) iegūšanai no ss.com lapām. Tā ļauj viegli atrast un apstrādāt HTML elementus, kas satur mums interesējošo informāciju.

### **re**

Regulāro izteiksmju bibliotēka, kas palīdz meklēt un apstrādāt tekstus, piemēram, izvilkt skaitļus no teksta vai pārbaudīt, vai tekstā ir konkrēti atslēgvārdi.

### **pandas**

Izmanto datu strukturētai glabāšanai un CSV faila izveidei ar visiem atrastajiem auto datiem. Pandas ļauj ērti veikt datu analīzi un saglabāt rezultātus tālākai apstrādei.

### **tabulate**

Izmanto, lai ērti un pārskatāmi izvadītu rezultātus tabulas formā konsolē. Tas padara rezultātu lasīšanu daudz ērtāku un saprotamāku.

## Paša definētas datu struktūras

Projektā tiek izmantota paša definēta klase `SSAutoScraper`, kas satur visas galvenās funkcijas datu iegūšanai, apstrādei un salīdzināšanai.

Katra auto sludinājuma dati tiek glabāti vārdnīcā (dictionary) ar šādiem laukiem:

-   `marka`
-   `modelis`
-   `gads`
-   `dzinējs`
-   `ātrumkārba`
-   `nobraukums`
-   `cena`
-   `saite`

Šī struktūra ļauj ērti apstrādāt un salīdzināt dažādu auto sludinājumu datus. Turklāt, lai nodrošinātu datu pārskatāmību un vieglu apstrādi, visi atrastie auto tiek apkopoti sarakstā, kas vēlāk tiek pārvērsts `pandas DataFrame` objektā un saglabāts CSV failā.

## Programmatūras izmantošanas metodes

### Nepieciešamo bibliotēku instalēšana:

Pirms programmas palaišanas nepieciešams uzstādīt nepieciešamās bibliotēkas:

```bash
pip install requests beautifulsoup4 pandas tabulate
```

### Programmas palaišana:

1.  Programma pieprasa ievadīt ss.com sludinājuma saiti ar sistu auto.
2.  Programma nolasa sludinājuma saturu, nosaka auto marku, modeli, gadu, dzinēju, nobraukumu un cenu.
3.  Programma izveido meklēšanas saiti uz ss.com ar tādu pašu marku un modeli, kā arī līdzīgu izlaiduma gadu (+/- 5 gadi).
4.  Tiek meklēti līdzīgi nesisti auto, un rezultāti tiek izvadīti tabulas veidā.
5.  Tiek veikts cenu salīdzinājums starp sisto un nesistajiem auto.
6.  Visi dati tiek saglabāti CSV failā, kuru var atvērt ar Excel vai citu tabulu redaktoru.

### Rezultātu interpretācija:

-   Konsolē tiek izvadīta informācija par sisto auto un atrastajiem nesistajiem auto.
-   Tiek parādīts cenu salīdzinājums (vidējā, minimālā, maksimālā cena).
-   Visi dati tiek saglabāti CSV failā, kas ļauj lietotājam tos analizēt arī vēlāk.
-   Ja sludinājumā nav norādīta marka vai modelis, programma var nespēt izveidot meklēšanas saiti.
