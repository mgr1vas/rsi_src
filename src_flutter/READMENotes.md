# Developer Notes / Expected Behaviour

## IMPORTANT:
Για την ώρα που δεν υπάρχουν αληθινά δεδομένα, δεν θα υπάρχει κάποιο `.env` αρχείο η κάποιο secret environment. Υπάρχουν mock data σε μορφή `.json`.

### Αρχική Οθόνη
Η εφαρμογή ανοίγει στον **χάρτη της Ελλάδας**, όπου εμφανίζονται τα accident markers από τα mock δεδομένα. Ο χρήστης πρέπει να μπορεί να κάνει zoom, pan και tap στα markers.
### Accident Markers
Τα markers πρέπει να δημιουργούνται από τα δεδομένα και όχι να είναι hardcoded. Σε πολλές κοντινές εγγραφές προτείνεται clustering ώστε να μην υπερφορτώνεται ο χάρτης.

### Navigation
Η πλοήγηση πρέπει να ξεκινά απευθείας από την αρχική οθόνη μέσω του navigation overlay / CTA. Δεν πρέπει να απαιτείται άνοιγμα του burger menu.

### Explore Mode
Πριν ξεκινήσει η πλοήγηση μπορούν να εμφανίζονται:
* Accident markers
* Accident details
* Destination search
* Safety information
* Suggested car rentals

### Drive Mode
Μόλις ξεκινήσει η πλοήγηση, το UI πρέπει να απλοποιείται και να δίνει προτεραιότητα σε:
* Route
* Current location
* Navigation instruction
* Safety alerts
* ETA / distance

### Safety Alerts
Όταν ο χρήστης πλησιάζει risk zone, να εμφανίζεται visual + audio warning. Το ίδιο warning δεν πρέπει να επαναλαμβάνεται συνεχώς σε κάθε GPS update και πρέπει να εξαφανίζεται αφού περάσει η περιοχή.

### Demo Drive / Simulation
Το Demo Drive πρέπει να χρησιμοποιεί όσο γίνεται το **ίδιο navigation UI και safety logic** με την πραγματική πλοήγηση, ώστε να λειτουργεί ως σωστό testing/demo mode.

### Car Rental Cards
Τα rental cards πρέπει να φορτώνονται στον χρήστη σαν καρουζέλ. Να επισημαίνονται καθαρά ως **Sponsored / Partner**.

### Commercial Content
Τα rental ads δεν πρέπει να εμφανίζονται πάνω από navigation instructions ή safety alerts και ιδανικά να εξαφανίζονται κατά την ενεργή πλοήγηση.

### Performance
Ο χάρτης πρέπει να παραμένει ομαλός. Να αποφεύγονται άσκοπα rebuilds και υπερβολική απόδοση πολλών markers ταυτόχρονα.

### Error States
Η εφαρμογή πρέπει να χειρίζεται σωστά:
* GPS unavailable
* Location permission denied
* No internet
* Accident data unavailable
* Rental data unavailable
* Route unavailable

### Βασική Προτεραιότητα
**ΑΣΦΑΛΕΙΑ → ΠΛΟΗΓΗΣΗ → ΠΛΗΡΟΦΟΡΙΕΣ → ΕΜΠΟΡΙΚΟ ΠΕΡΙΕΧΟΜΕΝΟ**
Για το event, προτεραιότητα έχει το flow:
**Open App → View Accident Map → Tap Marker → Search Destination → Start Navigation → Demo Drive → Safety Alert → Continue Route**
