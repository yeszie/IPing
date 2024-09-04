IPing – Zdalny monitoring z rozproszonych lokalizacji

IPing to rozwiązanie umożliwiające monitorowanie urządzeń i usług z różnych lokalizacji. System wspiera licencjonowanie oraz wysyłanie powiadomień poprzez e-mail i SMS.

Cel projektu
Celem programu IPing jest informowanie użytkownika o awariach lub niedostępności monitorowanych urządzeń lub usług za pomocą powiadomień SMS lub e-mail. Wyniki monitoringu są dostępne na bieżąco na portalu WWW. Na stronie publicznej, bez logowania, prezentowane są dane dotyczące urządzeń demonstracyjnych, natomiast po zalogowaniu użytkownik ma dostęp do monitoringu swoich indywidualnych lokalizacji.

Zasada działania
System działa poprzez cykliczne sprawdzanie dostępności urządzeń lub usług, odczytując dane z pliku konfiguracyjnego, który zawiera adresy IP i numery portów. Dane te są wysyłane na serwer znajdujący się w infrastrukturze IPing, a portal WWW pobiera i wizualizuje te informacje w czasie rzeczywistym. W przypadku niedostępności urządzenia lub lokalizacji, system automatycznie wysyła powiadomienie SMS lub e-mail.

Konfiguracja monitoringu
Przykładowy plik konfiguracyjny zawiera następujące informacje:

Adres IP lub domena urządzenia.
Numer portu (lub wartość 0 w przypadku sprawdzania przez ICMP/ping).
Opis urządzenia zdefiniowany przez użytkownika.
Dodatkowy opis, również określany przez użytkownika.
Każdy z tych parametrów jest wyświetlany na portalu w celu łatwej identyfikacji monitorowanych urządzeń.

Szybka konfiguracja klienta
Aby uruchomić monitoring, użytkownik końcowy uruchamia program monitorujący oraz edytuje plik konfiguracyjny, dodając urządzenia, które chce monitorować. Monitorować można wszystkie urządzenia z adresem IP, które odpowiadają na ping lub mają otwarte porty usługowe – na przykład komputery, urządzenia sieciowe, sterowniki elektryczne, routery, switche, kamery, rejestratory, systemy kontroli dostępu i inne.

Bezpieczeństwo i kompatybilność
Komunikacja z serwerem jest szyfrowana przy użyciu protokołu SSL, co zapewnia bezpieczeństwo przesyłanych danych. Program działa na systemach Windows i Linux, a wymagania sprzętowe są minimalne – wystarczy komputer z funkcją uruchamiania polecenia ping. Program może działać zarówno na fizycznym urządzeniu, jak i w środowisku wirtualnym. Transfer danych jest minimalny, ponieważ przesyłane są tylko informacje o dostępności lub niedostępności monitorowanych urządzeń.

Inteligentne algorytmy powiadamiania
System IPing zawiera wbudowane algorytmy, które decydują, kiedy należy poinformować użytkownika o niedostępności urządzenia. Przerwy między sprawdzeniami dostępności są elastyczne i można je dostosować w zależności od potrzeb monitorowanego systemu. Na przykład, jeśli w hotelu monitorowanych jest 200 urządzeń, a połączenie internetowe zostanie zerwane, system wykryje brak danych od tych urządzeń i wyśle powiadomienie po krótkim czasie (domyślnie 2 minuty). W przypadku całkowitej niedostępności lokalizacji, dodatkowe alerty dotyczące poszczególnych urządzeń nie będą już wysyłane.

Przykład działania
Dostępność lokalizacji: Jeśli zdalna lokalizacja jest dostępna (Internet działa poprawnie, a program monitorujący działa), a wybrana usługa lub host stanie się niedostępny, użytkownik otrzyma powiadomienie e-mail.
Alerty SMS: Alerty SMS domyślnie dotyczą całej lokalizacji (agenta), a nie poszczególnych usług czy hostów.
Więcej informacji na temat projektu można znaleźć na stronie IPing.pl.