import csv
import re
from datetime import datetime


class FormatoInvalidoError(Exception):
    pass


def validar_email(email):
    return bool(re.fullmatch(r"^[\w.-]+@[\w.-]+\.[A-Za-z]{2,}$", email))


def validar_cpf(cpf):
    return bool(re.fullmatch(r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$", cpf))


def validar_telefone(telefone):
    return bool(re.fullmatch(
        r"^(?:\(?\d{2}\)?\s?)?(?:9?\d{4})-?\d{4}$",
        telefone
    ))


def validar_data(data):
    if not re.fullmatch(r"^\d{2}/\d{2}/\d{4}$", data):
        return False

    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def validar_registro(registro):
    validacoes = {
        "email": validar_email,
        "cpf": validar_cpf,
        "telefone": validar_telefone,
        "data": validar_data
    }

    for campo, funcao in validacoes.items():
        if campo not in registro:
            raise KeyError(campo)

        if not funcao(registro[campo]):
            raise FormatoInvalidoError(f"Campo inválido: {campo}")


def analisar_arquivo(nome_arquivo):
    validos = []
    invalidos = []
    total = 0

    try:
        with open(nome_arquivo, "r", encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.DictReader(arquivo)

            if not leitor.fieldnames:
                raise ValueError("Arquivo vazio ou sem cabeçalho.")

            leitor.fieldnames = [
                coluna.strip().lower() for coluna in leitor.fieldnames
            ]

            obrigatorios = {"email", "cpf", "telefone", "data"}
            faltantes = obrigatorios - set(leitor.fieldnames)

            if faltantes:
                raise KeyError(", ".join(sorted(faltantes)))

            for numero, registro in enumerate(leitor, start=2):
                total += 1
                registro = {
                    chave.strip().lower(): (valor or "").strip()
                    for chave, valor in registro.items()
                    if chave is not None
                }

                try:
                    validar_registro(registro)
                    validos.append((numero, registro))
                except (FormatoInvalidoError, KeyError) as erro:
                    invalidos.append((numero, registro, str(erro)))

    except FileNotFoundError:
        print(f"Erro: arquivo '{nome_arquivo}' não encontrado.")
        return None

    except ValueError as erro:
        print(f"Erro de valor: {erro}")
        return None

    except KeyError as erro:
        print(f"Erro: coluna obrigatória ausente: {erro}")
        return None

    except UnicodeDecodeError:
        print("Erro: problema na codificação do arquivo.")

    else:
        print("Arquivo lido com sucesso!")
        return total, validos, invalidos

    finally:
        print("Leitura finalizada.")


def gerar_relatorio(resultado):
    if resultado is None:
        return

    total, validos, invalidos = resultado
    percentual = len(validos) / total * 100 if total else 0

    print("\n===== RELATÓRIO FINAL =====")
    print(f"Total de registros: {total}")
    print(f"Registros válidos: {len(validos)}")
    print(f"Registros inválidos: {len(invalidos)}")
    print(f"Percentual válido: {percentual:.1f}%")

    print("\n--- REGISTROS VÁLIDOS ---")
    for numero, registro in validos:
        print(f"Linha {numero}: {registro}")

    print("\n--- REGISTROS INVÁLIDOS ---")
    for numero, registro, motivo in invalidos:
        print(f"Linha {numero}: {registro}")
        print(f"Motivo: {motivo}")


def main():
    nome_arquivo = input(
        "Nome do arquivo CSV (Enter para dados.csv): "
    ).strip() or "dados.csv"

    resultado = analisar_arquivo(nome_arquivo)
    gerar_relatorio(resultado)


if __name__ == "__main__":
    main()