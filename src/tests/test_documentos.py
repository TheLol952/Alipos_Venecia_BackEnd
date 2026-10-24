import unittest

from src.servicios.documentos import (
    TIPO_DOCUMENTO_INTERNO,
    TIPO_DTE,
    identificar_documento,
    nombre_archivo_seguro,
)


class DocumentosTest(unittest.TestCase):
    def test_identifica_dte_del_ministerio_de_hacienda(self):
        data = {
            "identificacion": {
                "codigoGeneracion": "1AC28DF3-6D16-4B92-A427-0174C3B9E505",
                "numeroControl": "DTE-03-00000000-000000000000001",
            },
            "resumen": {},
        }

        self.assertEqual(
            identificar_documento(data),
            (TIPO_DTE, "1AC28DF3-6D16-4B92-A427-0174C3B9E505"),
        )

    def test_identifica_documento_interno_de_viaticos(self):
        data = {
            "version": 1,
            "estado": "FIRMADO",
            "egreso": {
                "ID_EGRESO": 12,
                "CORRELATIVO": "MV-2026-000004",
                "TIPO_DOCUMENTO": "MV",
                "NOMBRE_TIPO_DOCUMENTO": "Vale Simple de Pasaje Administrativo",
                "TOTAL_GASTOS": "1.75",
                "DETALLES": [],
            },
            "firma": {"nombre_firmante": "BLANCA AZUCENA MARTINEZ ALVARADO"},
        }

        self.assertEqual(
            identificar_documento(data),
            (TIPO_DOCUMENTO_INTERNO, "MV-2026-000004"),
        )

    def test_rechaza_json_que_no_es_documento_admitido(self):
        with self.assertRaisesRegex(ValueError, "estructura DTE"):
            identificar_documento({"mensaje": "contenido ajeno"})

    def test_genera_nombre_seguro_sin_permitir_rutas(self):
        self.assertEqual(
            nombre_archivo_seguro("../../MV 2026/000004"),
            "MV_2026_000004",
        )


if __name__ == "__main__":
    unittest.main()
