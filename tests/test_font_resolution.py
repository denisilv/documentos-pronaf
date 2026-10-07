import os
import unittest


class FontResolutionTest(unittest.TestCase):
    def test_existing_windows_font_candidate_is_selected(self):
        # Este teste reproduz a peça que o código precisa ter para escolher
        # um arquivo de fonte em um caminho Windows de maneira segura.
        from geradores import _candidate_font_path

        font_dir = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "Fonts")
        arial_path = os.path.join(font_dir, "arial.ttf")
        fallback_path = os.path.join(font_dir, "arialbd.ttf")

        # Simula o caso em que o primeiro caminho não existe e o segundo existe.
        chosen = _candidate_font_path(os.path.join(font_dir, "missing.ttf"), arial_path)
        self.assertEqual(chosen, arial_path)

    def test_no_existing_font_candidate_returns_none(self):
        from geradores import _candidate_font_path

        font_dir = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "Fonts")
        missing_a = os.path.join(font_dir, "missing_regular.ttf")
        missing_b = os.path.join(font_dir, "missing_bold.ttf")

        chosen = _candidate_font_path(missing_a, missing_b)
        self.assertIsNone(chosen)

    def test_cli_entrypoint_script_exists(self):
        from pathlib import Path
        self.assertTrue(Path("gerar_documentos.py").exists())

    def test_example_generation_api_exists(self):
        import geradores
        self.assertTrue(hasattr(geradores, "DADOS_EXEMPLO"))
        self.assertTrue(callable(getattr(geradores, "gerar_todos", None)))


if __name__ == "__main__":
    unittest.main()
