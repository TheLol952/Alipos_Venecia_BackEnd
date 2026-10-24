import unittest
from datetime import date
from unittest.mock import patch

import main


class MainTest(unittest.TestCase):
    def test_convierte_fecha_valida(self):
        self.assertEqual(main.convertir_fecha("2026-10-19"), date(2026, 10, 19))

    def test_rechaza_fecha_invalida(self):
        with self.assertRaisesRegex(ValueError, "no es válida"):
            main.convertir_fecha("19/10/2026")

    @patch("main.process_emails")
    def test_rango_final_es_inclusivo(self, process_emails):
        process_emails.return_value = None

        main.ejecutar_rango(date(2026, 10, 1), date(2026, 10, 19))

        process_emails.assert_called_once_with("2026-10-01", "2026-10-20")

    def test_rechaza_rango_invertido(self):
        with self.assertRaisesRegex(ValueError, "fecha inicial"):
            main.ejecutar_rango(date(2026, 10, 20), date(2026, 10, 19))

    @patch("main.ejecutar_rango")
    def test_argumentos_de_rango(self, ejecutar_rango):
        resultado = main.main(["--desde", "2026-10-01", "--hasta", "2026-10-19"])

        self.assertEqual(resultado, 0)
        ejecutar_rango.assert_called_once_with(date(2026, 10, 1), date(2026, 10, 19))


if __name__ == "__main__":
    unittest.main()
