
# XMODEM

Zasada działania protokołu XModem jest bardzo prosta:
- Transmisja jest inicjowana przez odbiornik, który wysyła znak NAK w odstępach co 10
sekund przez okres jednej minuty. W tym czasie nadajnik musi rozpocząć przesyłanie
pierwszego bloku danych
- Transferowany plik dzieli się na bloki o długości 128 bajtów, • bloki, na które podzielony
został plik, transmituje się kolejno jeden za drugim po otrzymaniu potwierdzenia
poprawności przesłania poprzedniego bloku
- Każdy przesyłany blok zaopatrywany jest w nagłówek składający się ze znaku SOH, numeru
bloku (1 bajt) oraz dopełnienia tego bloku do 255 ( 255 – numer bloku)
- Po przesłaniu nagłówka dokonywane jest przesłanie bloku danych, a następnie sumy
kontrolnej (checksum) definiowanej jako suma algebraiczna poszczególnych bajtów danych
bez przeniesienia (w wersji podstawowej protokołu),
- W trakcie odbierania bloku odbiornik wylicza sumę kontrolną, a następnie porównuje ją z
sumą obliczoną przez nadajnik. Jeżeli obie sumy kontrolne zgadzają się, odbiornik wysyła
potwierdzenie znakiem ACK, co dla nadajnika jest sygnałem do przesłania następnego bloku
danych. W przypadku, gdy sumy kontrolne wyliczone przez odbiornik i nadajnik są różne,
odbiornik wysyła znak NAK i nadajnik ponawia transmisję błędnie przesłanego bloku
danych
- Po przesłaniu ostatniego bajtu danych nadajnik wysyła znak EOT i ewentualnie ponawia
wysyłanie EOT do otrzymania potwierdzenia znakiem ACK ze strony odbiornika


Podane znaki sterujące posiadają następujące definicje:

SOH 01H
EOT 04H
ACK 06H
NAK 15H
CAN 18H
C 43H

## Baudrate

- https://en.wikipedia.org/wiki/Serial_port // baud
- https://en.wikipedia.org/wiki/Baud
- https://www.electronicdesign.com/technologies/communications/article/21802272/whats-the-difference-between-bit-rate-and-baud-rate

# CRC

Rozszerzenie CRC w odróżnieniu od pierwotnej wersji protokołu wykorzystuje lepszą 16-
bitową kontrolę błędów za pomocą algorytmu CRC do sprawdzania poprawności bloku danych.
Xmodem jest inicjowany przez odbiornik. Oznacza to, że odbiorca wysyła początkowy znak NAK
dla podstawowej wersji lub "C" dla wersji z sumą CRC do nadawcy wskazując, że jest gotowy do
odbierania danych w odpowiednim trybie. Następnie nadawca wysyła pakiet 132 lub 133 bajtów,
odbiorca sprawdza go i odpowiada znakiem ACK lub NAK, w którym to czasie nadawca wysyła
następny pakiet lub ponownie wysyła poprzedni pakiet. Proces ten trwa tak długo, aż odbiornik
odbierze znak EOT , na który odpowie znakiem ACK.

## Trochę więcej

Kiedy sekwencje bajtów są przesyłane z jednego miejsca do drugiego potrzebujemy znać informację
czy dane zostały odebrane bez błędów? Można temu zaradzić dodając do każdego bajta informacji
jeden bit kontrolny. Ale jak łatwo sobie wyobrazić prawdopodobieństwo wykrycia przekłamania jest
niewielkie. Szeroko stosowanym rozwiązaniem jest zastosowanie wielobitowego uogólnienia kontroli
parzystości zwanym CRC („Cyclic Redundancy Check”). W typowych aplikacjach CRC jest liczbą
dwubajtową, co oznacza, że prawdopodobieństwo nie wykrycia błędu wynosi (1/2)^16.

CRC jest metodą obliczania krótkich wartości kontrolnych dla długich ciągów bitów, pozwalających na
wykrycie błędów powstałych w nich podczas transmisji przez sieci lub zapisu na nośniki. Niewielkie
CRC jest dołączane do przesyłanych danych, tak by odbiorca mógł powtórzyć obliczenia dla
otrzymanej przesyłki i porównać wynik z załączonym.
CRC jest resztą z binarnego dzielenia ciągu danych przez relatywnie krótki dzielnik, zwany
generatorem lub wielomianem CRC. W praktyce stosuje się najczęściej wielomiany o długości 17 lub
33 bitów, dające odpowiednio wyniki 16 (CRC-16) i 32 bitów (CRC-32).
Metoda ta jest szeroko wykorzystywana do wykrywania błędów przypadkowych, ale nie nadaje się do
ochrony integralności w zastosowaniach kryptograficznych. CRC jest relatywnie łatwe do
sfałszowania, tj. jest możliwe takie poprawienie ciągu bitów by dawał on w wyniku poprawne CRC.
